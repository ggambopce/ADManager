# app/routers/admin_ads.py
from math import ceil
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status

from sqlalchemy.orm import Session

from app.schemas.common import ApiResponse
from app.schemas.ad import (
    AdResponse,
    AdPageResponse,
    AdCreate,
    AdUpdate,
)
from app.core.session import get_current_admin
from app.core.database import get_db
from app.services.ad_service import AdService

router = APIRouter(tags=["admin-ads"])


@router.post("/admin/ads", response_model=ApiResponse[AdResponse])
async def create_ad(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    target_url: Optional[str] = Form(None),
    image: UploadFile = File(...),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    광고 등록
    - 이미지 파일 저장
    - (선택) 숏링크 생성 로직은 나중에 AdService 안에서 확장
    """
    # 1) 이미지 저장
    image_url = AdService.save_image(image)

    # 2) 생성 DTO 구성
    create_dto = AdCreate(
        title=title,
        description=description,
        target_url=target_url,
    )

    # 3) DB Insert
    ad = AdService.create_ad(db, create_dto, image_url=image_url)

    return ApiResponse(
        code=200,
        message="광고 등록 성공",
        result=AdResponse.model_validate(ad),
    )


@router.get("/admin/ads", response_model=ApiResponse[AdPageResponse])
async def list_ads(
    page: int = 0,
    size: int = 10,
    keyword: Optional[str] = None,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    광고 목록 + 검색
    """
    ads, total = AdService.list_ads(db, page=page, size=size, keyword=keyword)
    total_pages = ceil(total / size) if size > 0 else 1

    page_res = AdPageResponse(
        content=[AdResponse.model_validate(ad) for ad in ads],
        page=page,
        size=size,
        total_elements=total,
        total_pages=total_pages,
    )

    return ApiResponse(
        code=200,
        message="광고 목록 조회 성공",
        result=page_res,
    )


@router.get("/admin/ads/{ad_id}", response_model=ApiResponse[AdResponse])
async def get_ad(
    ad_id: int,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    광고 단건 조회
    """
    ad = AdService.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="광고를 찾을 수 없습니다.",
        )

    return ApiResponse(
        code=200,
        message="광고 단건 조회 성공",
        result=AdResponse.model_validate(ad),
    )


@router.patch("/admin/ads/{ad_id}", response_model=ApiResponse[AdResponse])
async def update_ad(
    ad_id: int,
    body: AdUpdate,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    광고 수정 (JSON 기반 부분 업데이트)
    - 이미지까지 PATCH 하고 싶으면 별도 엔드포인트로 빼거나 multipart 처리 추가
    """
    ad = AdService.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="광고를 찾을 수 없습니다.",
        )

    update_data = body.model_dump(exclude_unset=True)
    updated = AdService.update_ad(db, ad, update_data)

    return ApiResponse(
        code=200,
        message="광고 수정 성공",
        result=AdResponse.model_validate(updated),
    )


@router.delete("/admin/ads/{ad_id}", response_model=ApiResponse[None])
async def delete_ad(
    ad_id: int,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    광고 삭제 (soft delete: is_active = False)
    """
    ad = AdService.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="광고를 찾을 수 없습니다.",
        )

    AdService.delete_ad(db, ad)

    return ApiResponse(
        code=200,
        message="광고 삭제 성공",
        result=None,
    )
