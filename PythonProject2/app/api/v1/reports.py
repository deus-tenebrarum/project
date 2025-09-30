from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
import json
import os
import tempfile

from app.core.database import get_db
from app.services.report_generator import ReportGenerator
from app.schemas.report import ReportRequest, ReportResponse

router = APIRouter()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
        request: ReportRequest,
        db: AsyncSession = Depends(get_db)
):
    """Генерация отчета по полетам"""
    generator = ReportGenerator(db)

    try:
        if request.format == "json":
            report_data = await generator.generate_json_report(
                start_date=request.start_date,
                end_date=request.end_date,
                regions=request.regions
            )

            # Сохранение в временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
                file_path = f.name

            return {
                "status": "success",
                "file_path": file_path,
                "format": "json",
                "size_bytes": os.path.getsize(file_path)
            }

        elif request.format == "png":
            chart_path = await generator.generate_chart(
                chart_type=request.chart_type or "bar",
                start_date=request.start_date,
                end_date=request.end_date
            )

            return {
                "status": "success",
                "file_path": chart_path,
                "format": "png",
                "size_bytes": os.path.getsize(chart_path)
            }

        else:
            raise HTTPException(400, "Неподдерживаемый формат отчета")

    except Exception as e:
        raise HTTPException(500, f"Ошибка генерации отчета: {str(e)}")


@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """Скачивание сгенерированного отчета"""
    # В продакшене здесь должна быть логика работы с хранилищем файлов
    # Для демонстрации возвращаем заглушку
    file_path = f"/tmp/{report_id}"

    if not os.path.exists(file_path):
        raise HTTPException(404, "Отчет не найден")

    return FileResponse(
        path=file_path,
        media_type='application/octet-stream',
        filename=os.path.basename(file_path)
    )