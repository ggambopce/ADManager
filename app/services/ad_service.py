import os
import random
import logging
import json
from datetime import datetime

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.ad import Ad
from app.core.config import settings

log = logging.getLogger("ad_service")

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

    # -------------------------
    # 2) buly 단축URL 생성
    # -------------------------
    @staticmethod
    def _create_short_url_with_buly(org_url: str) -> str | None:
        """
        buly 단축링크 생성.
        실패하면 None 반환.
        """
        if not org_url:
            return None

        try:
            payload = {
                "customer_id": settings.buly_customer_id,
                "partner_api_id": settings.buly_partner_api_id,
                "org_url": org_url,
            }

            # x-www-form-urlencoded 이므로 data= 사용
            resp = httpx.post(
                settings.buly_api_url,
                data=payload,
                timeout=5.0,
            )
            resp.raise_for_status()

            # 일부 환경에서 문자열로 내려올 수도 있으니 방어적으로 처리
            data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else json.loads(resp.text)

            # 예시: {"result":"Y","message":"성공적으로 생성하였습니다.","url":"https://buly.kr/uRIBxG"}
            if data.get("result") == "Y":
                return data.get("url")

            # 실패 메시지는 로그만 남기고 None 리턴
            log.warning(f"Buly shorturl failed: {data}")
            return None

        except Exception as e:
            # log.exception("Buly shorturl exception")
            return None    

    @staticmethod
    def create_ad(db: Session, data, image_url: str):
        """
        광고 생성 로직
        - image_url: save_image 로 저장한 경로
        - short_url 은 오직 buly API로 생성
        """
        # 1) buly 단축링크 생성 시도
        short_url = AdService._create_short_url_with_buly(data.target_url)

        # 2) 실패 시 target_url 그대로 사용
        if not short_url:
            short_url = data.target_url


        ad = Ad(
            title=data.title,
            description=data.description,
            image_url=image_url,
            target_url=data.target_url,
            short_url=short_url,
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
            
        )

        ads = query.all()
        if not ads:
            return None

        return random.choice(ads)
