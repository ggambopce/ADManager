# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.database import engine
from app.models import Base

from app.routers import admin_auth, admin_ads, public_ads

app = FastAPI()

# DB 테이블 생성 (개발 단계에서만 사용)
Base.metadata.create_all(bind=engine)

# 정적 파일: / → static/index.html
app.mount(
    "/static",  # 루트에 마운트 ("/static"으로 하고 싶으면 바꿔도 됨)
    StaticFiles(directory="static", html=True),
    name="static",
)

# API 라우터
app.include_router(admin_auth.router, prefix="/api")
app.include_router(admin_ads.router, prefix="/api")
app.include_router(public_ads.router, prefix="/api")