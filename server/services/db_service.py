"""
Database Service.
Manages the MongoDB connection and provides CRUD helpers
for the users, analyses, hairstyles, and tryons collections.
"""

from pymongo import MongoClient, DESCENDING
from bson import ObjectId


class DatabaseService:
    """MongoDB connection manager and CRUD operations."""

    def __init__(self, mongo_uri):
        """
        Initialize the MongoDB client and database reference.
        
        Args:
            mongo_uri: MongoDB connection string (e.g., mongodb://localhost:27017/faceshape).
        """
        self.client = MongoClient(mongo_uri)
        self.db = self.client.get_default_database()
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create performance-critical indexes if they don't exist."""
        try:
            self.db.users.create_index('email', unique=True)
            self.db.analyses.create_index([('user_id', 1), ('created_at', DESCENDING)])
            self.db.hairstyles.create_index([('face_shapes', 1), ('gender', 1)])
            self.db.hairstyles.create_index('slug', unique=True)
            self.db.hairstyles.create_index('tags')
            self.db.tryons.create_index('created_at', expireAfterSeconds=86400)
        except Exception:
            # Indexes may already exist; safe to ignore
            pass

    # ── Users ──────────────────────────────────────────────

    def create_user(self, user_doc):
        """Insert a new user document. Returns the inserted ID."""
        result = self.db.users.insert_one(user_doc)
        return result.inserted_id

    def find_user_by_email(self, email):
        """Find a user by email address."""
        return self.db.users.find_one({'email': email.lower().strip()})

    def find_user_by_id(self, user_id):
        """Find a user by ObjectId."""
        return self.db.users.find_one({'_id': ObjectId(user_id)})

    def update_user(self, user_id, update_fields):
        """Update specific fields on a user document."""
        return self.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_fields}
        )

    # ── Analyses ───────────────────────────────────────────

    def create_analysis(self, analysis_doc):
        """Insert a new analysis record. Returns the inserted ID."""
        result = self.db.analyses.insert_one(analysis_doc)
        return result.inserted_id

    def find_analysis_by_id(self, analysis_id):
        """Find an analysis by ID."""
        if not analysis_id or not ObjectId.is_valid(analysis_id):
            return None
        return self.db.analyses.find_one({'_id': ObjectId(analysis_id)})

    def find_analyses_by_user(self, user_id, search_query=None, face_shape=None,
                              start_date=None, end_date=None, page=1, limit=10):
        """
        Paginated query for a user's analysis history with search and filter capabilities.
        
        Args:
            user_id: User's ObjectId or string ID.
            search_query: Optional string to search across face_shape, recommendations, and AI advice.
            face_shape: Optional face shape filter.
            start_date: Optional datetime start boundary.
            end_date: Optional datetime end boundary.
            page: Page number.
            limit: Page size.
        
        Returns:
            tuple: (list of analysis docs, total count)
        """
        query = {'user_id': ObjectId(user_id)}

        if face_shape:
            query['face_shape'] = face_shape.lower()

        if search_query:
            regex = {'$regex': search_query, '$options': 'i'}
            query['$or'] = [
                {'face_shape': regex},
                {'recommendations.name': regex},
                {'selected_hairstyle.name': regex},
                {'ai_advice': regex}
            ]

        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter['$gte'] = start_date
            if end_date:
                date_filter['$lte'] = end_date
            query['created_at'] = date_filter

        total = self.db.analyses.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.db.analyses.find(query) \
            .sort('created_at', DESCENDING) \
            .skip(skip) \
            .limit(limit)
        return list(cursor), total

    def update_analysis_selected_hairstyle(self, analysis_id, user_id, selected_hairstyle_doc):
        """Record or update user's chosen hairstyle for a specific analysis."""
        return self.db.analyses.update_one(
            {'_id': ObjectId(analysis_id), 'user_id': ObjectId(user_id)},
            {'$set': {'selected_hairstyle': selected_hairstyle_doc}}
        )

    def delete_analysis(self, analysis_id, user_id):
        """Delete an analysis if it belongs to the user."""
        return self.db.analyses.delete_one({
            '_id': ObjectId(analysis_id),
            'user_id': ObjectId(user_id)
        })

    def clear_user_history(self, user_id):
        """Delete all analysis history records for a user."""
        return self.db.analyses.delete_many({'user_id': ObjectId(user_id)})

    # ── Hairstyles ─────────────────────────────────────────

    def find_hairstyles(self, face_shape=None, gender=None, hair_type=None,
                        hair_length=None, category=None, maintenance_level=None,
                        min_popularity=None, page=1, limit=20):
        """
        Query the hairstyle catalog with comprehensive metadata filters.
        
        Returns:
            tuple: (list of hairstyle docs, total count)
        """
        query = {}
        if face_shape:
            query['face_shapes'] = face_shape
        if gender and gender != 'unisex':
            query['gender'] = {'$in': [gender, 'unisex']}
        if hair_type:
            query['hair_types'] = hair_type
        if hair_length:
            query['hair_length'] = hair_length
        if category:
            query['category'] = category
        if maintenance_level:
            query['maintenance_level'] = maintenance_level
        if min_popularity is not None:
            query['popularity'] = {'$gte': int(min_popularity)}

        total = self.db.hairstyles.count_documents(query)
        skip = (page - 1) * limit
        cursor = self.db.hairstyles.find(query).skip(skip).limit(limit)
        return list(cursor), total

    def find_hairstyle_by_id(self, hairstyle_id):
        """Find a single hairstyle by ID."""
        return self.db.hairstyles.find_one({'_id': ObjectId(hairstyle_id)})

    def find_hairstyle_by_slug(self, slug):
        """Find a hairstyle by its URL slug."""
        return self.db.hairstyles.find_one({'slug': slug})

    def increment_view_count(self, hairstyle_id):
        """Increment the view count for a hairstyle."""
        self.db.hairstyles.update_one(
            {'_id': ObjectId(hairstyle_id)},
            {'$inc': {'view_count': 1}}
        )

    # ── Try-Ons ────────────────────────────────────────────

    def create_tryon(self, tryon_doc):
        """Insert a virtual try-on record. Returns the inserted ID."""
        result = self.db.tryons.insert_one(tryon_doc)
        return result.inserted_id

    def find_tryon_by_id(self, tryon_id):
        """Find a try-on record by ID."""
        return self.db.tryons.find_one({'_id': ObjectId(tryon_id)})

    # ── Utility ────────────────────────────────────────────

    def close(self):
        """Close the MongoDB client connection."""
        self.client.close()
