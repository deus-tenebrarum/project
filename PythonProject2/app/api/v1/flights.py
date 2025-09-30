from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from typing import List, Optional
from typing import Dict, Any

from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.models.flight import Flight
from app.services.parser import TelegramParser
from app.services.geo_service import GeoService
from app.services.excel_parser import ExcelParser
from app.schemas.flight import FlightCreate, FlightResponse, FlightStatistics

router = APIRouter()


@router.post("/upload/shr", response_model=Dict[str, Any])
async def upload_shr_messages(
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db)
):
    """Загрузка и обработка SHR телеграмм"""
    if file.content_type not in ["application/json", "text/plain", "application/xml"]:
        raise HTTPException(400, "Неподдерживаемый формат файла")

    content = await file.read()
    parser = TelegramParser()
    geo_service = GeoService()

    processed = 0
    errors = []

    # Парсинг в зависимости от формата
    # Здесь упрощенная логика для демонстрации
    messages = content.decode('utf-8').split('\n')

    for msg in messages:
        if 'SHR-' in msg:
            try:
                parsed = parser.parse_shr_message(msg)

                if parsed['dep_coords']:
                    dep_region = geo_service.get_region_by_coordinates(
                        parsed['dep_coords'][0],
                        parsed['dep_coords'][1]
                    )
                else:
                    dep_region = None

                if parsed['arr_coords']:
                    arr_region = geo_service.get_region_by_coordinates(
                        parsed['arr_coords'][0],
                        parsed['arr_coords'][1]
                    )
                else:
                    arr_region = None

                # Создание записи в БД
                flight = Flight(
                    sid=parsed['sid'],
                    flight_date=parsed['date'],
                    dep_coords=str(parsed['dep_coords']) if parsed['dep_coords'] else None,
                    arr_coords=str(parsed['arr_coords']) if parsed['arr_coords'] else None,
                    dep_region=dep_region,
                    arr_region=arr_region,
                    operator=parsed['operator'],
                    uav_type=parsed['uav_type'],
                    uav_reg=parsed['registration'],
                    raw_shr=msg
                )

                db.add(flight)
                processed += 1

            except Exception as e:
                errors.append(f"Ошибка обработки: {str(e)}")

    await db.commit()

    return {
        "processed": processed,
        "errors": errors,
        "status": "success" if processed > 0 else "failed"
    }


@router.post("/upload/excel", response_model=Dict[str, Any])
async def upload_excel_file(
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db)
):
    """Загрузка и обработка Excel файла с полетными данными"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "Требуется Excel файл")

    # Сохранение временного файла
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        parser = ExcelParser()
        flights_data = parser.parse_flight_data(tmp_path)

        geo_service = GeoService()
        processed = 0

        for flight_data in flights_data:
            if flight_data.get('dep_coords_parsed'):
                dep_region = geo_service.get_region_by_coordinates(
                    flight_data['dep_coords_parsed'][0],
                    flight_data['dep_coords_parsed'][1]
                )
            else:
                dep_region = None

            flight = Flight(
                flight_date=flight_data['date'],
                dep_coords=flight_data.get('dep_coords'),
                arr_coords=flight_data.get('arr_coords'),
                dep_region=dep_region,
                uav_type=flight_data.get('aircraft_type'),
                uav_reg=flight_data.get('aircraft')
            )

            db.add(flight)
            processed += 1

        await db.commit()

    finally:
        os.unlink(tmp_path)

    return {
        "processed": processed,
        "status": "success"
    }


@router.get("/", response_model=List[FlightResponse])
async def get_flights(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        region: Optional[str] = None,
        db: AsyncSession = Depends(get_db)
):
    """Получение списка полетов с фильтрацией"""
    query = select(Flight)

    conditions = []
    if start_date:
        conditions.append(Flight.flight_date >= start_date)
    if end_date:
        conditions.append(Flight.flight_date <= end_date)
    if region:
        conditions.append(
            (Flight.dep_region == region) | (Flight.arr_region == region)
        )

    if conditions:
        query = query.where(and_(*conditions))

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    flights = result.scalars().all()

    return flights


@router.get("/statistics", response_model=FlightStatistics)
async def get_flight_statistics(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: AsyncSession = Depends(get_db)
):
    """Получение статистики по полетам"""
    query = select(
        func.count(Flight.id).label('total_flights'),
        func.avg(Flight.duration_minutes).label('avg_duration'),
        func.count(func.distinct(Flight.operator)).label('unique_operators'),
        func.count(func.distinct(Flight.uav_type)).label('unique_uav_types')
    )

    if start_date:
        query = query.where(Flight.flight_date >= start_date)
    if end_date:
        query = query.where(Flight.flight_date <= end_date)

    result = await db.execute(query)
    stats = result.first()

    return {
        "total_flights": stats.total_flights or 0,
        "avg_duration_minutes": float(stats.avg_duration or 0),
        "unique_operators": stats.unique_operators or 0,
        "unique_uav_types": stats.unique_uav_types or 0,
        "period_start": start_date,
        "period_end": end_date
    }