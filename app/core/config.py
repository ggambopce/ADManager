from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    애플리케이션 전역 설정 값을 관리하는 클래스.
    - .env 파일에 정의된 환경변수를 읽어서 필드에 매핑한다.
    - 여기서 session_cookie_name, session_expire_seconds, Redis 설정 등이
      세션 기반 로그인에 직접 사용된다.
    """
    # ===== 앱 기본 설정 =====
    app_env: str = "local"           # APP_ENV
    app_name: str = "ad-server"      # APP_NAME

    # ===== DB 설정 =====
    db_host: str = "127.0.0.1"       # DB_HOST
    db_port: int = 3306              # DB_PORT
    db_user: str = "user"            # DB_USER
    db_password: str = "1234"        # DB_PASSWORD
    db_name: str = "admanager_mariadb"  # DB_NAME

    # ===== Redis 설정 =====
    redis_host: str = "127.0.0.1"    # REDIS_HOST
    redis_port: int = 6379           # REDIS_PORT
    redis_db: int = 0                # REDIS_DB
    redis_password: str | None = None

    # ===== 세션 설정 =====
    # 관리자 세션 쿠키 이름.
    # 브라우저에는 이 이름으로 session_id가 저장된다.
    session_cookie_name: str = "admin_session"  # SESSION_COOKIE_NAME
    session_expire_seconds: int = 8640000000    # SESSION_EXPIRE_SECONDS

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # .env에 정의는 돼 있지만 모델에 없는 값이 있어도 무시하고 싶으면 ignore
        extra="ignore",
        # 엄격하게 하고 싶으면 위 줄을 extra="forbid" 로 바꾸고
        # .env에 있는 키들을 전부 필드로 정의해주면 된다.
    )
    # ===== buly API 설정 =====
    buly_api_url: str = "https://www.buly.kr/api/shoturl.siso"  # BULY_API_URL
    buly_customer_id: str = "205341530"                        # BULY_CUSTOMER_ID
    buly_partner_api_id: str = "6131D27090895F3699A6B4D9F9B67023"


settings = Settings()
