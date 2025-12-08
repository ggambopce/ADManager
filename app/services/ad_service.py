import os
import random
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.ad import Ad


class AdService:

    @staticmethod
    def save_image(upload_file, upload_dir="static/ads"):
        """이미지 파일을 저장하고 경로를 반환한다."""
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"{datetime.now().timestamp()}_{upload_file.filename}"
        file_path = os.path.join(upload_dir, filename)

        with open(file_path, "wb") as f:
            f.write(upload_file.file.read())

        return f"/static/ads/{filename}"

    @staticmethod
    def create_ad(db: Session, data, image_url: str):
        ad = Ad(
            title=data.title,
            description=data.description,
            image_url=image_url,
            target_url=data.target_url,
            short_url=data.short_url,
            start_at=data.start_at,
            end_at=data.end_at,
            is_active=True,
        )
        db.add(ad)
        db.commit()
        db.refresh(ad)
        return ad

    @staticmethod
    def get_ad(db: Session, ad_id: int):
        ad = db.query(Ad).filter(Ad.id == ad_id, Ad.is_active == True).first()
        return ad

    @staticmethod
    def list_ads(db: Session, page: int, size: int, keyword: str | None):
        query = db.query(Ad).filter(Ad.is_active == True)

        if keyword:
            query = query.filter(
                or_(
                    Ad.title.like(f"%{keyword}%"),
                    Ad.description.like(f"%{keyword}%")
                )
            )

        total = query.count()
        ads = (
            query.order_by(Ad.created_at.desc())
            .offset(page * size)
            .limit(size)
            .all()
        )

        return ads, total

    @staticmethod
    def update_ad(db: Session, ad: Ad, update_data: dict):
        for key, value in update_data.items():
            setattr(ad, key, value)

        db.commit()
        db.refresh(ad)
        return ad

    @staticmethod
    def delete_ad(db: Session, ad: Ad):
        ad.is_active = False
        db.commit()

    @staticmethod
    def random_ad(db: Session):
        now = datetime.now()
        query = db.query(Ad).filter(
            Ad.is_active == True,
            or_(Ad.start_at == None, Ad.start_at <= now),
            or_(Ad.end_at == None, Ad.end_at >= now),
        )

        ads = query.all()
        if not ads:
            return None

        return random.choice(ads)
