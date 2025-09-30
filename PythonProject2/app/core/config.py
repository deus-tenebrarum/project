from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # База данных
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/bas_flights"

    # Redis для кэша
    REDIS_URL: str = "redis://localhost:6379/0"

    # API настройки
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "БАС Полеты"
    VERSION: str = "1.0.0"

    # Безопасность
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 неделя

    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]

    # Файлы
    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB

    # Логирование
    LOG_LEVEL: str = "INFO"

    # Внешние сервисы
    GIS_API_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

