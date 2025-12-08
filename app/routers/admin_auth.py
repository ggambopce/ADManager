# app/routers/admin_auth.py
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response, Request

from sqlalchemy.orm import Session

from app.schemas.common import ApiResponse
from app.schemas.admin import AdminLoginRequest, AdminMeResponse
from app.core.database import get_db
from app.core.redis_client import get_redis
from app.core.session import get_current_admin, delete_admin_session
from app.services.admin_auth_service import AdminAuthService

router = APIRouter(tags=["admin-auth"])


@router.post("/admin/login", response_model=ApiResponse[dict])
async def admin_login(
    req: AdminLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
):
    # 실제 로그인 로직은 전부 Service 로 위임
    admin = await AdminAuthService.login(
        db=db,
        login_id=req.loginId,
        password=req.password,
        response=response,
        redis=redis,
    )

    return ApiResponse(
        code=200,
        message="로그인 성공",
        result={"username": admin.login_id},
    )


@router.post("/auth/logout", response_model=ApiResponse[None])
async def logout(
    request: Request,
    response: Response,
    redis=Depends(get_redis),
):
    # 세션 삭제도 유틸 함수로 위임
    await delete_admin_session(request, response, redis)

    return ApiResponse(code=200, message="로그아웃 완료", result=None)


@router.get("/admin/me", response_model=ApiResponse[AdminMeResponse])
async def me(
    current_admin=Depends(get_current_admin),
):
    """
    현재는 세션에 loginId 만 있으니 createdAt 은 일단 now 기준으로 세팅.
    나중에 DB에서 AdminUser 조회해서 진짜 createdAt을 넣으면 됨.
    """
    info = AdminAuthService.get_admin_info_from_session(current_admin)

    dto = AdminMeResponse(
        loginId=info["loginId"],
        createdAt=datetime.now(timezone.utc),
    )
    return ApiResponse(
        code=200,
        message="로그인 관리자 정보",
        result=dto,
    )
