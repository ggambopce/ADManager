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
    """
    관리자 로그인 엔드포인트.
    [요청]
    - body: { "loginId": "...", "password": "..." }
    [동작]
    1) AdminAuthService.login(...) 호출로
       - DB 에서 관리자 계정 조회
       - 비밀번호 검증
       - 세션 생성 + admin_session 쿠키 설정
    2) 로그인 성공 시, 응답 JSON + Set-Cookie 헤더를 반환한다.
    [결과]
    - 이후 브라우저는 admin_session 쿠키를 들고 요청하게 되고,
      관리자 전용 API에서는 get_current_admin Depends로 세션을 확인한다.
    """
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
    """
    관리자 로그아웃 엔드포인트.
    [동작]
    1) 요청 쿠키에서 admin_session(세션 ID)을 읽는다.
    2) Redis 에서 해당 세션 키를 삭제한다.
    3) 브라우저 쿠키도 제거한다.
    이렇게 하면 이후 요청에서는 세션이 존재하지 않으므로
    /admin/me 같은 엔드포인트 호출 시 401 UNAUTHORIZED 를 받게 된다.
    """
    # 세션 삭제도 유틸 함수로 위임
    await delete_admin_session(request, response, redis)

    return ApiResponse(code=200, message="로그아웃 완료", result=None)


@router.get("/admin/me", response_model=ApiResponse[AdminMeResponse])
async def me(
    current_admin=Depends(get_current_admin),
):
    """
    현재 로그인한 관리자 정보 조회 엔드포인트.
    [동작]
    1) get_current_admin 이 쿠키 + Redis 세션을 검증한다.
    2) 검증에 성공하면 세션에 저장된 loginId 를 바탕으로
       AdminAuthService.get_admin_info_from_session(...) 에서 필요한 정보를 구성한다.
    3) 현재는 예시로 createdAt 을 now 기준으로 내려주고,
       추후 DB에서 실제 계정 생성일을 가져와 내려주는 식으로 확장할 수 있다.
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
