from fastapi import APIRouter
from app.schemas.common import ApiResponse
from app.schemas.ad import AdResponse

router = APIRouter(tags=["public-ads"])


@router.get("/public/ad", response_model=ApiResponse[AdResponse])
async def random_ad():
    # TODO: DB에서 유효기간 내 광고 랜덤 추출
    ad = AdResponse(
        id=1,
        title="겨울 세일",
        description="전 상품 최대 50% 할인",
        image_url="https://ads.example.com/static/ads/1_abcdef.jpg",
        target_url="https://origin.com",
        short_url="https://buly.kr/xxx",
        start_at=None,
        end_at=None,
    )
    return ApiResponse(code=200, message="광고 조회 성공", result=ad)
