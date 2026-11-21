"""
Recommendation Service.
Matches a detected face shape to suitable hairstyles in MongoDB,
applies multi-attribute user preference filtering, and ranks results by compatibility.
"""

from server.models.hairstyle import HairstyleModel


class RecommendationService:
    """Face shape → hairstyle matching, filtering, and multi-criteria ranking engine."""

    # 7 Target Face Shape Affinity Matrix (compatibility between face shapes)
    SHAPE_AFFINITY = {
        'oval':     {'oval': 1.0, 'round': 0.65, 'heart': 0.75, 'oblong': 0.60, 'square': 0.55, 'diamond': 0.65, 'triangle': 0.60},
        'round':    {'round': 1.0, 'oval': 0.70, 'heart': 0.55, 'oblong': 0.60, 'square': 0.45, 'diamond': 0.50, 'triangle': 0.50},
        'square':   {'square': 1.0, 'oval': 0.65, 'round': 0.45, 'oblong': 0.55, 'heart': 0.50, 'diamond': 0.55, 'triangle': 0.65},
        'heart':    {'heart': 1.0, 'oval': 0.75, 'round': 0.55, 'oblong': 0.55, 'square': 0.45, 'diamond': 0.65, 'triangle': 0.45},
        'oblong':   {'oblong': 1.0, 'oval': 0.65, 'round': 0.55, 'square': 0.55, 'heart': 0.55, 'diamond': 0.45, 'triangle': 0.45},
        'diamond':  {'diamond': 1.0, 'oval': 0.75, 'heart': 0.65, 'round': 0.50, 'oblong': 0.45, 'square': 0.55, 'triangle': 0.55},
        'triangle': {'triangle': 1.0, 'oval': 0.70, 'square': 0.65, 'diamond': 0.55, 'round': 0.50, 'oblong': 0.45, 'heart': 0.45},
    }

    def __init__(self, db_service):
        """
        Args:
            db_service: DatabaseService instance.
        """
        self.db = db_service

    def get_recommendations(self, face_shape, gender=None, hair_type=None,
                            hair_length=None, category=None, maintenance_level=None,
                            min_popularity=None, limit=10):
        """
        Find, filter, and rank hairstyles for a detected face shape.
        
        Strategy:
            1. Query primary hairstyles matching the face shape and metadata filters.
            2. Compute multi-criteria ranking compatibility score (0-1.0 or 0-100%).
            3. Fall back to secondary shape matches if primary results are sparse.
            4. Rank results descending by compatibility score and rating.
        
        Args:
            face_shape: Detected face shape string (oval, round, square, heart, diamond, oblong).
            gender: Filter by gender ('male', 'female', 'unisex').
            hair_type: Filter by texture ('straight', 'wavy', 'curly', 'coily').
            hair_length: Filter by length ('short', 'medium', 'long').
            category: Filter by style category ('classic', 'modern', 'edgy', 'formal', 'casual', 'trending').
            maintenance_level: Filter by maintenance level ('low', 'medium', 'high').
            min_popularity: Minimum popularity threshold (0-100).
            limit: Maximum number of ranked recommendations to return.
        
        Returns:
            list: Ranked hairstyle dicts with added 'compatibility' score.
        """
        # Primary query: exact shape match + filters
        hairstyles, _ = self.db.find_hairstyles(
            face_shape=face_shape,
            gender=gender,
            hair_type=hair_type,
            hair_length=hair_length,
            category=category,
            maintenance_level=maintenance_level,
            min_popularity=min_popularity,
            limit=limit * 2
        )

        # Compute compatibility scores
        results = []
        for hs in hairstyles:
            compatibility = self._compute_compatibility(
                face_shape, hs,
                target_length=hair_length,
                target_category=category,
                target_maintenance=maintenance_level
            )
            hs_response = HairstyleModel.to_response(hs)
            hs_response['compatibility'] = compatibility
            results.append(hs_response)

        # Secondary match fallback if few primary matches found
        if len(results) < limit:
            affinities = self.SHAPE_AFFINITY.get(face_shape.lower(), {})
            for alt_shape, affinity in sorted(affinities.items(), key=lambda x: -x[1]):
                if alt_shape == face_shape.lower() or affinity < 0.5:
                    continue
                alt_styles, _ = self.db.find_hairstyles(
                    face_shape=alt_shape,
                    gender=gender,
                    hair_type=hair_type,
                    hair_length=hair_length,
                    category=category,
                    maintenance_level=maintenance_level,
                    min_popularity=min_popularity,
                    limit=limit
                )
                for hs in alt_styles:
                    hs_id = str(hs['_id'])
                    if not any(r['id'] == hs_id for r in results):
                        compatibility = self._compute_compatibility(
                            face_shape, hs,
                            target_length=hair_length,
                            target_category=category,
                            target_maintenance=maintenance_level
                        )
                        hs_response = HairstyleModel.to_response(hs)
                        hs_response['compatibility'] = compatibility
                        results.append(hs_response)
                if len(results) >= limit:
                    break

        # Sort by compatibility score descending, then avg_rating, then popularity
        results.sort(key=lambda x: (-x['compatibility'], -x.get('avg_rating', 0), -x.get('popularity', 0)))

        return results[:limit]

    def _compute_compatibility(self, face_shape, hairstyle_doc,
                               target_length=None, target_category=None, target_maintenance=None):
        """
        Multi-criteria Ranking Algorithm:
        - Base Shape Affinity (0.75-0.85)
        - User Rating Bonus (up to 0.08)
        - Popularity Score Bonus (up to 0.05)
        - Preference Match Bonus (length, category, maintenance - up to 0.05)
        """
        score = 0.0
        face_shape_lower = face_shape.lower() if face_shape else 'oval'
        doc_shapes = [s.lower() for s in hairstyle_doc.get('face_shapes', [])]

        if face_shape_lower in doc_shapes:
            score += 0.85
        else:
            affinities = self.SHAPE_AFFINITY.get(face_shape_lower, {})
            best_aff = max([affinities.get(s, 0.4) for s in doc_shapes], default=0.4)
            score += best_aff * 0.80

        # Rating Bonus (0-5 scale -> up to 0.08)
        rating = hairstyle_doc.get('avg_rating', 4.0)
        score += (rating / 5.0) * 0.08

        # Popularity Bonus (0-100 scale -> up to 0.05)
        popularity = hairstyle_doc.get('popularity', 85)
        score += (popularity / 100.0) * 0.05

        # Preference Match Bonus
        bonus = 0.0
        if target_length and hairstyle_doc.get('hair_length') == target_length:
            bonus += 0.02
        if target_category and hairstyle_doc.get('category') == target_category:
            bonus += 0.015
        if target_maintenance and hairstyle_doc.get('maintenance_level') == target_maintenance:
            bonus += 0.015
        score += bonus

        return round(min(score, 1.0), 2)
