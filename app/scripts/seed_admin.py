# app/scripts/seed_admin.py

from sqlalchemy.orm import Session
import bcrypt

from app.core.database import SessionLocal
from app.models.admin import AdminUser


def hash_password(plain: str) -> str:
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def main():
    db: Session = SessionLocal()

    try:
        existing = db.query(AdminUser).filter(AdminUser.login_id == "admin").first()
        if existing:
            print("관리자 계정 이미 존재")
            return

        raw_password = "1234"
        hashed = hash_password(raw_password)

        admin = AdminUser(
            login_id="admin",
            password_hash=hashed,
        )
        db.add(admin)
        db.commit()

        print("===== 관리자 계정 생성 완료 =====")
        print("loginId: admin")
        print("password: 1234")

    finally:
        db.close()


if __name__ == "__main__":
    main()
