"""
Run this once to seed the database with:
- Admin user
- Sample blocks and zones
- Sample categories

Usage: python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, create_tables
from app.models.user import User
from app.models.block import Block
from app.models.delivery_zone import DeliveryZone
from app.models.category import Category
from app.core.security import hash_password

def seed():
    create_tables()
    db = SessionLocal()

    # Admin user
    admin = db.query(User).filter(User.email == "admin@localmart.com").first()
    if not admin:
        admin = User(
            name="Admin",
            email="admin@localmart.com",
            phone="9999999999",
            password_hash=hash_password("admin123"),
            role="admin",
            email_verified=True,
        )
        db.add(admin)
        print("✅ Admin created: admin@localmart.com / admin123")
    else:
        if not admin.email_verified:
            admin.email_verified = True
            print("✅ Admin email_verified set to True")
        print("ℹ️  Admin already exists")

    # Blocks
    block_data = [
        {"name": "Block A - Gandhi Nagar", "description": "Near Gandhi Chowk"},
        {"name": "Block B - Nehru Colony", "description": "Near Nehru Park"},
        {"name": "Block C - Market Area", "description": "Main market area"},
        {"name": "Block D - Station Road", "description": "Near railway station"},
    ]
    blocks = []
    for bd in block_data:
        b = db.query(Block).filter(Block.name == bd["name"]).first()
        if not b:
            b = Block(**bd)
            db.add(b)
            db.flush()
            print(f"✅ Block created: {bd['name']}")
        blocks.append(b)

    db.flush()

    # Zones for each block
    for block in blocks:
        existing_zones = db.query(DeliveryZone).filter(DeliveryZone.block_id == block.id).count()
        if existing_zones == 0:
            zones = [
                DeliveryZone(block_id=block.id, zone_name=f"{block.name} - Zone 1", delivery_charge=20, min_order_value=200),
                DeliveryZone(block_id=block.id, zone_name=f"{block.name} - Zone 2", delivery_charge=30, min_order_value=300),
            ]
            db.add_all(zones)
            print(f"✅ Zones added for {block.name}")

    # Categories
    import re
    def slugify(text):
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        return re.sub(r"[\s_-]+", "-", text)

    categories = ["Vegetables", "Fruits", "Dairy", "Bakery", "Beverages", "Snacks", "Household", "Personal Care"]
    for cname in categories:
        slug = slugify(cname)
        cat = db.query(Category).filter(Category.slug == slug).first()
        if not cat:
            db.add(Category(name=cname, slug=slug))
            print(f"✅ Category: {cname}")

    db.commit()
    db.close()
    print("\n🎉 Seed complete!")

if __name__ == "__main__":
    seed()
