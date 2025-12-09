from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.common import ApiResponse
from app.schemas.ad import PublicAdResponse
from app.core.database import get_db
from app.services.ad_service import AdService

router = APIRouter(tags=["public-ads"])


@router.get("/public/ad", response_model=ApiResponse[PublicAdResponse])
async def random_ad(db: Session = Depends(get_db)):
    """
    여러 백엔드 서버에서 공용으로 사용하는 랜덤 광고 조회 API.

    - is_active=True
    - (start_at <= now <= end_at) 또는 기간 미설정
    중에서 랜덤 1개 선택.
    """
    ad = AdService.random_ad(db)
    if not ad:
        # 유효한 광고가 1개도 없을 때
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_ACTIVE_AD",
        )

    dto = PublicAdResponse(
        id=ad.id,
        title=ad.title,
        description=ad.description,
        image_url=ad.image_url,
        short_url=ad.short_url,
        target_url=ad.target_url,
    )

    return ApiResponse(
        code=200,
        message="광고 조회 성공",
        result=dto,
    )
