"""Seed default users into the database.

Creates:
  - admin@nflfantasy.local / Admin1234 (role: admin)
  - manager@nflfantasy.local / Manager1234 (role: manager)
  - user@nflfantasy.local / User1234 (role: user)
"""
from datetime import datetime

from ..config.database import SessionLocal
from ..config.auth import get_password_hash
from ..modules.users.models import User

DEFAULT_USERS = [
    {
        "name": "Admin User",
        "email": "admin@nflfantasy.local",
        "alias": "admin",
        "password": "Admin1234",
        "role": "admin",
    },
    {
        "name": "Manager User",
        "email": "manager@nflfantasy.local",
        "alias": "manager",
        "password": "Manager1234",
        "role": "manager",
    },
    {
        "name": "Normal User",
        "email": "user@nflfantasy.local",
        "alias": "user",
        "password": "User1234",
        "role": "user",
    },
]


def seed_users():
    db = SessionLocal()
    try:
        created = 0
        skipped = 0
        for u in DEFAULT_USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                skipped += 1
                continue
            user = User(
                name=u["name"],
                email=u["email"],
                alias=u["alias"],
                hashed_password=get_password_hash(u["password"]),
                role=u["role"],
                account_status="active",
                created_at=datetime.utcnow(),
            )
            db.add(user)
            created += 1
        db.commit()
        print(f"Seed completed. Created: {created}, Skipped (already existed): {skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
