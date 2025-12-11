# app/routers/page_ads.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=["pages-ads"])


@router.get("/ads", response_class=HTMLResponse)
async def ads_list_page(request: Request):
    """
    광고 목록 페이지 (목록 데이터는 JS 가 /api/admin/ads 로 요청)
    """
    return templates.TemplateResponse(
        "ads/list.html",
        {"request": request},
    )


@router.get("/ads/new", response_class=HTMLResponse)
async def ads_new_page(request: Request):
    """
    광고 등록 페이지
    """
    return templates.TemplateResponse(
        "ads/form.html",
        {"request": request, "mode": "create", "ad_id": None},
    )


@router.get("/ads/{ad_id}", response_class=HTMLResponse)
async def ads_detail_page(ad_id: int, request: Request):
    """
    광고 상세 페이지
    """
    return templates.TemplateResponse(
        "ads/detail.html",
        {"request": request, "ad_id": ad_id},
    )


@router.get("/ads/{ad_id}/edit", response_class=HTMLResponse)
async def ads_edit_page(ad_id: int, request: Request):
    """
    광고 수정 페이지
    """
    return templates.TemplateResponse(
        "ads/form.html",
        {"request": request, "mode": "edit", "ad_id": ad_id},
    )
