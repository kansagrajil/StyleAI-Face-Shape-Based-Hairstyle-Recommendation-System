"""
Hairstyle catalog data model.
Defines the schema for hairstyle entries in the MongoDB catalog.
"""

from datetime import datetime, timezone


class HairstyleModel:
    """Schema and helpers for the hairstyles collection."""

    COLLECTION = 'hairstyles'

    @staticmethod
    def create_document(name, slug, face_shapes, gender, hair_types,
                        description, image_url, hair_length='medium',
                        category='modern', maintenance_level='medium',
                        popularity=85, tags=None):
        """
        Build a new hairstyle catalog document with comprehensive metadata.
        
        Args:
            name: Display name of the hairstyle.
            slug: URL-friendly unique identifier.
            face_shapes: List of compatible face shapes (oval, round, square, heart, diamond, oblong).
            gender: 'male', 'female', or 'unisex'.
            hair_types: List of suitable hair textures (straight, wavy, curly, coily).
            description: Detailed description of the hairstyle.
            image_url: Path or URL to the hairstyle image.
            hair_length: 'short', 'medium', or 'long'.
            category: 'classic', 'modern', 'edgy', 'formal', 'casual', 'trending'.
            maintenance_level: 'low', 'medium', or 'high'.
            popularity: Numerical popularity score (0-100).
            tags: Optional list of searchable tags.
        
        Returns:
            dict: Hairstyle document.
        """
        return {
            'name': name,
            'slug': slug,
            'face_shapes': face_shapes,
            'gender': gender,
            'hair_types': hair_types,
            'hair_length': hair_length,
            'category': category,
            'maintenance_level': maintenance_level,
            'popularity': popularity,
            'description': description,
            'image_url': image_url,
            'tags': tags or [],
            'avg_rating': 4.5,
            'view_count': 100,
            'created_at': datetime.now(timezone.utc)
        }

    @staticmethod
    def to_response(doc):
        """Serialize a hairstyle document for API response."""
        return {
            'id': str(doc['_id']),
            'name': doc['name'],
            'slug': doc['slug'],
            'face_shapes': doc['face_shapes'],
            'gender': doc['gender'],
            'hair_types': doc.get('hair_types', []),
            'hair_length': doc.get('hair_length', 'medium'),
            'category': doc.get('category', 'modern'),
            'maintenance_level': doc.get('maintenance_level', 'medium'),
            'popularity': doc.get('popularity', 85),
            'description': doc['description'],
            'image_url': doc['image_url'],
            'tags': doc.get('tags', []),
            'avg_rating': doc.get('avg_rating', 4.5),
            'view_count': doc.get('view_count', 0)
        }
