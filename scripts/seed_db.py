"""
Seed the database with a test user.
Run: python scripts/seed_db.py
"""
import asyncio
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../services/api"))

from app.core.database import init_db, AsyncSessionLocal
from app.models.user import User


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        user = User(email="demo@example.com", name="Demo User")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"Created user: {user.id}")


if __name__ == "__main__":
    asyncio.run(seed())
