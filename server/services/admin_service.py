"""
Admin Management Service.
Handles system analytics, user management, hairstyle CRUD operations,
face shape category rules, and uploaded image management.
"""

import os
from bson import ObjectId
from pymongo import DESCENDING


class AdminService:
    """System administration service."""

    def __init__(self, db_service, upload_folder='server/uploads'):
        self.db_service = db_service
        self.db = db_service.db
        self.upload_folder = upload_folder

    # ── System Analytics ──────────────────────────────────────

    def get_system_analytics(self):
        """
        Compute real-time system analytics and statistics.
        
        Returns:
            dict: {
                'total_users': int,
                'active_users': int,
                'admin_users': int,
                'total_hairstyles': int,
                'total_scans': int,
                'total_tryons': int,
                'face_shape_distribution': dict,
                'top_hairstyles': list
            }
        """
        total_users = self.db.users.count_documents({})
        active_users = self.db.users.count_documents({'is_active': True})
        admin_users = self.db.users.count_documents({'role': 'admin'})

        total_hairstyles = self.db.hairstyles.count_documents({})
        total_scans = self.db.analyses.count_documents({})
        total_tryons = self.db.tryons.count_documents({})

        # Face shape distribution across all scans
        shapes = ['oval', 'round', 'square', 'heart', 'diamond', 'oblong']
        distribution = {shape: 0 for shape in shapes}

        pipeline = [
            {'$group': {'_id': '$face_shape', 'count': {'$sum': 1}}}
        ]
        results = list(self.db.analyses.aggregate(pipeline))

        for r in results:
            shape_key = str(r['_id']).lower() if r['_id'] else ''
            if shape_key in distribution:
                distribution[shape_key] = r['count']

        # Top 5 most viewed/rated hairstyles
        top_cursor = self.db.hairstyles.find().sort([('view_count', DESCENDING), ('avg_rating', DESCENDING)]).limit(5)
        top_hairstyles = [{
            'name': hs['name'],
            'views': hs.get('view_count', 0),
            'rating': hs.get('avg_rating', 4.5)
        } for hs in top_cursor]

        return {
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'total_hairstyles': total_hairstyles,
            'total_scans': total_scans,
            'total_tryons': total_tryons,
            'face_shape_distribution': distribution,
            'top_hairstyles': top_hairstyles
        }

    # ── User Management ────────────────────────────────────────

    def find_users(self, search_query=None, role=None, page=1, limit=20):
        """Find users with search, role filter, and pagination."""
        query = {}
        if role:
            query['role'] = role
        if search_query:
            regex = {'$regex': search_query, '$options': 'i'}
            query['$or'] = [{'name': regex}, {'email': regex}]

        total = self.db.users.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.db.users.find(query).sort('created_at', DESCENDING).skip(skip).limit(limit)

        users = []
        for u in cursor:
            users.append({
                'user_id': str(u['_id']),
                'name': u.get('name', ''),
                'email': u.get('email', ''),
                'gender': u.get('gender', 'other'),
                'role': u.get('role', 'user'),
                'is_active': u.get('is_active', True),
                'created_at': u.get('created_at').isoformat() if u.get('created_at') else ''
            })

        return users, total

    def update_user_status_or_role(self, user_id, role=None, is_active=None):
        """Update a user's role or account active status."""
        update = {}
        if role in ['admin', 'user']:
            update['role'] = role
        if is_active is not None:
            update['is_active'] = bool(is_active)

        if not update:
            return None

        return self.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update})

    def delete_user(self, user_id):
        """Delete a user account and associated scans."""
        obj_id = ObjectId(user_id)
        self.db.analyses.delete_many({'user_id': obj_id})
        self.db.tryons.delete_many({'user_id': obj_id})
        return self.db.users.delete_one({'_id': obj_id})

    # ── Hairstyle CRUD ────────────────────────────────────────

    def create_hairstyle(self, data):
        """Insert new hairstyle record."""
        doc = {
            'name': data['name'],
            'slug': data['slug'],
            'face_shapes': data.get('face_shapes', []),
            'gender': data.get('gender', 'unisex'),
            'hair_types': data.get('hair_types', []),
            'hair_length': data.get('hair_length', 'medium'),
            'category': data.get('category', 'modern'),
            'maintenance_level': data.get('maintenance_level', 'medium'),
            'popularity': int(data.get('popularity', 85)),
            'description': data.get('description', ''),
            'image_url': data.get('image_url', ''),
            'tags': data.get('tags', []),
            'avg_rating': float(data.get('avg_rating', 4.5)),
            'view_count': 0
        }
        res = self.db.hairstyles.insert_one(doc)
        return str(res.inserted_id)

    def update_hairstyle(self, hairstyle_id, data):
        """Update existing hairstyle record."""
        update = {
            'name': data['name'],
            'slug': data['slug'],
            'face_shapes': data.get('face_shapes', []),
            'gender': data.get('gender', 'unisex'),
            'hair_types': data.get('hair_types', []),
            'hair_length': data.get('hair_length', 'medium'),
            'category': data.get('category', 'modern'),
            'maintenance_level': data.get('maintenance_level', 'medium'),
            'popularity': int(data.get('popularity', 85)),
            'description': data.get('description', ''),
            'image_url': data.get('image_url', ''),
            'tags': data.get('tags', [])
        }
        return self.db.hairstyles.update_one({'_id': ObjectId(hairstyle_id)}, {'$set': update})

    def delete_hairstyle(self, hairstyle_id):
        """Delete hairstyle from catalog."""
        return self.db.hairstyles.delete_one({'_id': ObjectId(hairstyle_id)})

    # ── Uploaded Image Management ─────────────────────────────

    def list_uploaded_images(self):
        """List files in the uploads folder with file size and timestamp."""
        files = []
        if os.path.exists(self.upload_folder):
            for root, dirs, filenames in os.walk(self.upload_folder):
                for f in filenames:
                    filepath = os.path.join(root, f)
                    stat = os.stat(filepath)
                    rel_path = os.path.relpath(filepath, self.upload_folder).replace('\\', '/')
                    files.append({
                        'filename': f,
                        'rel_path': f"/uploads/{rel_path}",
                        'size_kb': round(stat.st_size / 1024, 1),
                        'modified_at': stat.st_mtime
                    })

        files.sort(key=lambda x: x['modified_at'], reverse=True)
        return files[:50]

    def delete_uploaded_image(self, rel_filename):
        """Delete an uploaded image file."""
        filepath = os.path.join(self.upload_folder, rel_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
