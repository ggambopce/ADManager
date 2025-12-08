from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "admanager-mariadb"

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    SESSION_PREFIX: str = "adserver:session:"
    SESSION_TTL: int = 86400

    class Config:
        env_file = ".env"


settings = Settings()
