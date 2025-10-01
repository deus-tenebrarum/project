from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, date

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import flights, regions, reports
from app.services.parser import TelegramParser
from app.services.geo_service import GeoService
from app.models.flight import Flight, FlightStatus

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("Инициализация БД и сервисов...")
    await init_db()
    yield
    logger.info("Завершение работы приложения")

app = FastAPI(
    title="Сервис анализа полетов БАС",
    description="API для обработки и анализа данных о полетах беспилотных авиационных систем",
    version="1.0.0",
    lifespan=lifespan
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(flights.router, prefix="/api/v1/flights", tags=["Полеты"])
app.include_router(regions.router, prefix="/api/v1/regions", tags=["Регионы"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Отчеты"])

# ДОПОЛНИТЕЛЬНО: Подключаем роутеры БЕЗ префикса /api/v1 для обратной совместимости
app.include_router(flights.router, prefix="/flights", tags=["Полеты (legacy)"], include_in_schema=False)
app.include_router(regions.router, prefix="/regions", tags=["Регионы (legacy)"], include_in_schema=False)
app.include_router(reports.router, prefix="/reports", tags=["Отчеты (legacy)"], include_in_schema=False)

# Корневой маршрут
@app.get("/")
async def root():
    """Корневой маршрут"""
    return {
        "message": "Сервис анализа полетов БАС",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api/v1"
    }

# Health check
@app.get("/health")
async def health():
    """Проверка здоровья сервиса"""
    return {"status": "healthy"}