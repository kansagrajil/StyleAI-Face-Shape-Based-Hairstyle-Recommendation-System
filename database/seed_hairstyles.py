"""
Hairstyle Catalog Seed Script.
Populates the MongoDB hairstyles collection with initial metadata-rich data for 6 face shapes:
Oval, Round, Square, Heart, Diamond, and Oblong.

Usage:
    python database/seed_hairstyles.py --force
"""

import os
import sys
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Hairstyle catalog organized by face shape compatibility & rich metadata
HAIRSTYLES = [
    # ── Oval Face Styles ─────────────────────────────────────
    {
        'name': 'Long Layered Waves',
        'slug': 'long-layered-waves',
        'face_shapes': ['oval', 'heart', 'oblong'],
        'gender': 'female',
        'hair_types': ['wavy', 'straight'],
        'hair_length': 'long',
        'category': 'romantic',
        'maintenance_level': 'medium',
        'popularity': 95,
        'description': 'Soft cascading layers that add volume and beautifully frame the face. Works great with both straight and wavy textures.',
        'image_url': '/assets/images/hairstyles/long-layered-waves.jpg',
        'tags': ['layered', 'long', 'romantic', 'versatile']
    },
    {
        'name': 'Classic Bob',
        'slug': 'classic-bob',
        'face_shapes': ['oval', 'heart', 'diamond'],
        'gender': 'female',
        'hair_types': ['straight', 'wavy'],
        'hair_length': 'short',
        'category': 'classic',
        'maintenance_level': 'low',
        'popularity': 90,
        'description': 'A timeless chin-length bob that highlights facial symmetry and adds structure to softer features.',
        'image_url': '/assets/images/hairstyles/classic-bob.jpg',
        'tags': ['bob', 'short', 'classic', 'professional']
    },
    {
        'name': 'Textured Pixie Cut',
        'slug': 'textured-pixie',
        'face_shapes': ['oval', 'heart'],
        'gender': 'female',
        'hair_types': ['straight', 'wavy', 'curly'],
        'hair_length': 'short',
        'category': 'edgy',
        'maintenance_level': 'low',
        'popularity': 88,
        'description': 'A bold, short pixie with textured layers on top. Shows off balanced facial features and bone structure.',
        'image_url': '/assets/images/hairstyles/textured-pixie.jpg',
        'tags': ['pixie', 'short', 'bold', 'modern']
    },
    # ── Round Face Styles ────────────────────────────────────
    {
        'name': 'Long Side-Swept Layers',
        'slug': 'long-side-swept-layers',
        'face_shapes': ['round', 'oval'],
        'gender': 'female',
        'hair_types': ['straight', 'wavy'],
        'hair_length': 'long',
        'category': 'modern',
        'maintenance_level': 'medium',
        'popularity': 92,
        'description': 'Long layers with a deep side part create asymmetry and vertical lines, elongating a round face shape.',
        'image_url': '/assets/images/hairstyles/long-side-swept.jpg',
        'tags': ['layered', 'long', 'side-part', 'slimming']
    },
    {
        'name': 'Lob with Face Framing',
        'slug': 'lob-face-framing',
        'face_shapes': ['round', 'square', 'oval'],
        'gender': 'female',
        'hair_types': ['straight', 'wavy'],
        'hair_length': 'medium',
        'category': 'trending',
        'maintenance_level': 'medium',
        'popularity': 94,
        'description': 'A long bob (lob) with face-framing layers that hit just below the chin, adding length to round faces.',
        'image_url': '/assets/images/hairstyles/lob-face-framing.jpg',
        'tags': ['lob', 'medium', 'face-framing', 'flattering']
    },
    # ── Square Face Styles ───────────────────────────────────
    {
        'name': 'Soft Waves with Side Part',
        'slug': 'soft-waves-side-part',
        'face_shapes': ['square', 'round'],
        'gender': 'female',
        'hair_types': ['wavy', 'straight'],
        'hair_length': 'medium',
        'category': 'classic',
        'maintenance_level': 'medium',
        'popularity': 89,
        'description': 'Soft, flowing waves with a side part soften strong jawlines and add feminine movement.',
        'image_url': '/assets/images/hairstyles/soft-waves-side.jpg',
        'tags': ['waves', 'medium', 'soft', 'feminine']
    },
    {
        'name': 'Layered Shag',
        'slug': 'layered-shag',
        'face_shapes': ['square', 'diamond', 'oval'],
        'gender': 'unisex',
        'hair_types': ['wavy', 'curly', 'straight'],
        'hair_length': 'medium',
        'category': 'edgy',
        'maintenance_level': 'low',
        'popularity': 87,
        'description': 'A modern shag cut with lots of layers that break up angular features and add texture.',
        'image_url': '/assets/images/hairstyles/layered-shag.jpg',
        'tags': ['shag', 'medium', 'textured', 'trendy']
    },
    # ── Heart Face Styles ────────────────────────────────────
    {
        'name': 'Chin-Length Bob',
        'slug': 'chin-length-bob',
        'face_shapes': ['heart', 'diamond'],
        'gender': 'female',
        'hair_types': ['straight', 'wavy'],
        'hair_length': 'short',
        'category': 'classic',
        'maintenance_level': 'medium',
        'popularity': 91,
        'description': 'A bob that ends at the chin adds width at the jawline, balancing a wider forehead.',
        'image_url': '/assets/images/hairstyles/chin-bob.jpg',
        'tags': ['bob', 'short', 'balancing', 'chic']
    },
    {
        'name': 'Side-Swept Bangs',
        'slug': 'side-swept-bangs',
        'face_shapes': ['heart', 'round', 'oval'],
        'gender': 'female',
        'hair_types': ['straight', 'wavy'],
        'hair_length': 'medium',
        'category': 'casual',
        'maintenance_level': 'medium',
        'popularity': 86,
        'description': 'Wispy side-swept bangs minimize a wider forehead while adding soft, flattering angles.',
        'image_url': '/assets/images/hairstyles/side-swept-bangs.jpg',
        'tags': ['bangs', 'any-length', 'soft', 'versatile']
    },
    # ── Oblong Face Styles ───────────────────────────────────
    {
        'name': 'Voluminous Curls',
        'slug': 'voluminous-curls',
        'face_shapes': ['oblong', 'oval', 'diamond'],
        'gender': 'female',
        'hair_types': ['curly', 'wavy', 'coily'],
        'hair_length': 'medium',
        'category': 'formal',
        'maintenance_level': 'high',
        'popularity': 93,
        'description': 'Full, bouncy curls add width to the sides, shortening the appearance of a longer face.',
        'image_url': '/assets/images/hairstyles/voluminous-curls.jpg',
        'tags': ['curls', 'medium', 'volume', 'glamorous']
    },
    # ── Diamond Face Styles ──────────────────────────────────
    {
        'name': 'Chin-Length Textured Cut',
        'slug': 'chin-textured-cut',
        'face_shapes': ['diamond', 'heart', 'oval'],
        'gender': 'unisex',
        'hair_types': ['straight', 'wavy', 'curly'],
        'hair_length': 'short',
        'category': 'modern',
        'maintenance_level': 'low',
        'popularity': 88,
        'description': 'A textured cut that adds fullness at the chin level, balancing wider cheekbones.',
        'image_url': '/assets/images/hairstyles/chin-textured.jpg',
        'tags': ['textured', 'short', 'balancing', 'edgy']
    },
    # ── Male Styles ──────────────────────────────────────────
    {
        'name': 'Classic Taper Fade',
        'slug': 'classic-taper-fade',
        'face_shapes': ['oval', 'square', 'diamond'],
        'gender': 'male',
        'hair_types': ['straight', 'wavy', 'curly'],
        'hair_length': 'short',
        'category': 'business',
        'maintenance_level': 'medium',
        'popularity': 96,
        'description': 'A clean taper fade with length on top. Versatile and professional-looking for most face shapes.',
        'image_url': '/assets/images/hairstyles/taper-fade.jpg',
        'tags': ['fade', 'short', 'classic', 'professional']
    },
    {
        'name': 'Textured Quiff',
        'slug': 'textured-quiff',
        'face_shapes': ['round', 'square', 'oval'],
        'gender': 'male',
        'hair_types': ['straight', 'wavy'],
        'hair_length': 'medium',
        'category': 'modern',
        'maintenance_level': 'medium',
        'popularity': 94,
        'description': 'A modern quiff with textured styling adds height and angular lines to round or square faces.',
        'image_url': '/assets/images/hairstyles/textured-quiff.jpg',
        'tags': ['quiff', 'medium', 'modern', 'stylish']
    },
    {
        'name': 'Side Part Pompadour',
        'slug': 'side-part-pompadour',
        'face_shapes': ['oblong', 'oval', 'square'],
        'gender': 'male',
        'hair_types': ['straight', 'wavy'],
        'hair_length': 'medium',
        'category': 'formal',
        'maintenance_level': 'high',
        'popularity': 91,
        'description': 'A polished pompadour with side part creates width at the top, ideal for longer face shapes.',
        'image_url': '/assets/images/hairstyles/side-part-pompadour.jpg',
        'tags': ['pompadour', 'medium', 'polished', 'classic']
    },
    {
        'name': 'Buzz Cut',
        'slug': 'buzz-cut',
        'face_shapes': ['oval', 'diamond', 'square'],
        'gender': 'male',
        'hair_types': ['straight', 'wavy', 'curly', 'coily'],
        'hair_length': 'short',
        'category': 'low-maintenance',
        'maintenance_level': 'low',
        'popularity': 90,
        'description': 'A clean, low-maintenance buzz cut that highlights strong facial features and bone structure.',
        'image_url': '/assets/images/hairstyles/buzz-cut.jpg',
        'tags': ['buzz', 'very-short', 'minimal', 'bold']
    },
    {
        'name': 'Medium Curly Top',
        'slug': 'medium-curly-top',
        'face_shapes': ['square', 'heart', 'oval', 'triangle'],
        'gender': 'male',
        'hair_types': ['curly', 'coily'],
        'hair_length': 'medium',
        'category': 'trending',
        'maintenance_level': 'medium',
        'popularity': 89,
        'description': 'Curly hair left longer on top with shorter sides adds softness to angular face shapes.',
        'image_url': '/assets/images/hairstyles/curly-top.jpg',
        'tags': ['curly', 'medium', 'natural', 'trendy']
    },
    # ── Triangle Face Styles ──────────────────────────────────
    {
        'name': 'Voluminous Crop with Side Fringe',
        'slug': 'voluminous-crop-side-fringe',
        'face_shapes': ['triangle', 'oval', 'diamond'],
        'gender': 'female',
        'hair_types': ['straight', 'wavy'],
        'hair_length': 'short',
        'category': 'modern',
        'maintenance_level': 'low',
        'popularity': 91,
        'description': 'Adds fullness at the crown and forehead to perfectly balance a wider jawline.',
        'image_url': '/assets/images/hairstyles/voluminous-crop.jpg',
        'tags': ['crop', 'fringe', 'modern', 'volume']
    },
    {
        'name': 'Textured Top Fade',
        'slug': 'textured-top-fade',
        'face_shapes': ['triangle', 'square', 'oval'],
        'gender': 'male',
        'hair_types': ['straight', 'wavy', 'curly'],
        'hair_length': 'short',
        'category': 'trending',
        'maintenance_level': 'medium',
        'popularity': 93,
        'description': 'Tapered sides with textured height on top draws vision upward from the jaw.',
        'image_url': '/assets/images/hairstyles/textured-top-fade.jpg',
        'tags': ['fade', 'textured', 'trendy', 'short']
    },
]


def seed(mongo_uri=None, force=False):
    """
    Seed the hairstyles collection in MongoDB with complete metadata.
    
    Args:
        mongo_uri: MongoDB connection string.
        force: If True, clear and seed without prompt.
    """
    uri = mongo_uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017/faceshape')
    client = MongoClient(uri)
    db = client.get_default_database()
    collection = db.hairstyles

    count = collection.count_documents({})
    if count > 0 and not force:
        confirm = input(f"Collection has {count} documents. Clear and re-seed? (y/N): ")
        if confirm.lower() != 'y':
            print("Aborted.")
            client.close()
            return

    collection.delete_many({})

    now = datetime.now(timezone.utc)
    for hs in HAIRSTYLES:
        hs['avg_rating'] = round(4.0 + (hash(hs['slug']) % 10) / 10.0, 1)
        hs['view_count'] = abs(hash(hs['slug'])) % 5000 + 500
        hs['created_at'] = now

    result = collection.insert_many(HAIRSTYLES)
    print(f"[SUCCESS] Seeded {len(result.inserted_ids)} metadata-rich hairstyles into MongoDB")

    # Create Indexes for efficient multi-attribute filtering
    collection.create_index([('face_shapes', 1), ('gender', 1)])
    collection.create_index([('hair_length', 1), ('category', 1)])
    collection.create_index('slug', unique=True)
    collection.create_index('tags')
    print("[SUCCESS] Indexes created for MongoDB hairstyle catalog")

    client.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Seed database hairstyles catalog.")
    parser.add_argument("--force", "-f", action="store_true", help="Force seeding without confirmation prompt.")
    parser.add_argument("--with-user", action="store_true", help="Also seed initial test user (user@example.com / user1234).")
    args = parser.parse_args()

    force_env = os.getenv('FORCE_SEED', 'false').lower() in ('true', '1', 'yes')
    seed(force=args.force or force_env)

    if args.with_user:
        from database.seed_user import seed_user
        seed_user(force=args.force or force_env)
