"""
Initial User Seed Script.
Seeds an initial test/default user account into MongoDB:
Email: user@example.com
Password: user1234

Usage:
    python database/seed_user.py
    python database/seed_user.py --force
    python database/seed_user.py --email admin@example.com --password adminpass --role admin
"""

import os
import sys
from datetime import datetime, timezone
from pymongo import MongoClient
import bcrypt
from dotenv import load_dotenv

load_dotenv()


def hash_password(plain_password: str) -> str:
    """Hash plaintext password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')


def seed_user(
    mongo_uri: str = None,
    email: str = "user@example.com",
    password: str = "user1234",
    name: str = "Initial User",
    gender: str = "female",
    role: str = "user",
    force: bool = False
):
    """
    Seed or update an initial user in the MongoDB database.

    Args:
        mongo_uri: MongoDB connection URI string.
        email: User email address.
        password: Plaintext password to hash and store.
        name: User display name.
        gender: User gender.
        role: Account role ('user' or 'admin').
        force: If True, overwrites/resets existing user's password.
    """
    uri = mongo_uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017/faceshape')
    client = MongoClient(uri)
    db = client.get_default_database()
    users_collection = db.users

    # Ensure unique index on email
    try:
        users_collection.create_index('email', unique=True)
    except Exception:
        pass

    clean_email = email.lower().strip()
    existing_user = users_collection.find_one({'email': clean_email})
    hashed_pwd = hash_password(password)

    if existing_user:
        if force:
            users_collection.update_one(
                {'_id': existing_user['_id']},
                {
                    '$set': {
                        'password_hash': hashed_pwd,
                        'name': name,
                        'gender': gender,
                        'role': role,
                        'updated_at': datetime.now(timezone.utc)
                    }
                }
            )
            print(f"[SUCCESS] Updated existing user password: {clean_email} (Password: {password})")
            client.close()
            return existing_user['_id']
        else:
            print(f"[INFO] User '{clean_email}' already exists in MongoDB. Use --force to update credentials.")
            client.close()
            return existing_user['_id']

    # Insert new user document
    user_doc = {
        'name': name,
        'email': clean_email,
        'password_hash': hashed_pwd,
        'gender': gender,
        'role': role,
        'preferences': {
            'hair_type': '',
            'hair_length': '',
            'style_preference': ''
        },
        'is_active': True,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }

    result = users_collection.insert_one(user_doc)
    print(f"[SUCCESS] Initial user created successfully!")
    print(f"          Email:    {clean_email}")
    print(f"          Password: {password}")
    print(f"          User ID:  {result.inserted_id}")

    client.close()
    return result.inserted_id


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Seed initial user into MongoDB.")
    parser.add_argument("--email", default="user@example.com", help="User email address")
    parser.add_argument("--password", default="user1234", help="User plaintext password")
    parser.add_argument("--name", default="Initial User", help="User display name")
    parser.add_argument("--gender", default="female", help="User gender")
    parser.add_argument("--role", default="user", help="User role (user or admin)")
    parser.add_argument("--force", "-f", action="store_true", help="Force update password if user already exists")
    args = parser.parse_args()

    seed_user(
        email=args.email,
        password=args.password,
        name=args.name,
        gender=args.gender,
        role=args.role,
        force=args.force
    )
