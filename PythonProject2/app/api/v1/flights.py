from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import json
import tempfile
import os

from app.core.database import get_db
from app.models.flight import Flight
from app.services.parser import TelegramParser
from app.services.geo_service import GeoService
from app.services.excel_parser import ExcelParser

router = APIRouter()


@router.post("/upload/excel", response_model=Dict[str, Any])
async def upload_excel_file(
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db)
):
    """
    Загрузка и обработка Excel файла с полетными данными.
    Поддерживает форматы:
    - 2024.xlsx: множественные листы с телеграммами SHR/DEP/ARR
    - 2025.xlsx: один лист Result_1 с данными центров ЕС ОрВД
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "Требуется Excel файл (.xlsx или .xls)")

    # Сохранение временного файла
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        parser = ExcelParser()
        geo_service = GeoService()
        
        # Парсим файл (обрабатывает все листы автоматически)
        flights_data = parser.parse_flight_data(tmp_path)
        
        processed = 0
        errors = []
        skipped = 0

        for flight_data in flights_data:
            try:
                # Геопривязка
                dep_region = None
                arr_region = None

                # Координаты могут быть в формате tuple или None
                if flight_data.get('dep_coords'):
                    coords = flight_data['dep_coords']
                    if isinstance(coords, tuple) and len(coords) == 2:
                        dep_region = geo_service.get_region_by_coordinates(coords[0], coords[1])

                if flight_data.get('arr_coords'):
                    coords = flight_data['arr_coords']
                    if isinstance(coords, tuple) and len(coords) == 2:
                        arr_region = geo_service.get_region_by_coordinates(coords[0], coords[1])

                # Проверка обязательных полей
                if not flight_data.get('date'):
                    skipped += 1
                    continue

                # Создание записи в БД
                flight = Flight(
                    sid=flight_data.get('sid'),
                    flight_date=flight_data.get('date'),
                    dep_time=flight_data.get('dep_time'),
                    arr_time=flight_data.get('arr_time'),
                    dep_coords=str(flight_data['dep_coords']) if flight_data.get('dep_coords') else None,
                    arr_coords=str(flight_data['arr_coords']) if flight_data.get('arr_coords') else None,
                    dep_region=dep_region or flight_data.get('region'),  # используем регион из названия листа
                    arr_region=arr_region,
                    operator=flight_data.get('operator'),
                    uav_type=flight_data.get('uav_type'),
                    uav_reg=flight_data.get('registration'),
                    duration_minutes=flight_data.get('duration_minutes'),
                    center_name=flight_data.get('center_name'),
                    raw_shr=flight_data.get('raw_shr'),
                    raw_dep=flight_data.get('raw_dep'),
                    raw_arr=flight_data.get('raw_arr'),
                    altitude_min=flight_data.get('altitude', {}).get('min') if flight_data.get('altitude') else None,
                    altitude_max=flight_data.get('altitude', {}).get('max') if flight_data.get('altitude') else None,
                    status='arrived' if flight_data.get('arr_time') else 'scheduled'
                )

                db.add(flight)
                processed += 1

            except Exception as e:
                error_msg = f"Ошибка обработки записи: {str(e)}"
                errors.append(error_msg)
                print(f"ERROR: {error_msg}")  # для отладки

        await db.commit()
        
        return {
            "processed": processed,
            "skipped": skipped,
            "errors": errors[:10] if errors else [],  # Ограничиваем 10 ошибками
            "total_flights": processed,
            "status": "success" if processed > 0 else "failed",
            "message": f"Обработано {processed} полетов из файла {file.filename}"
        }

    except Exception as e:
        raise HTTPException(500, f"Ошибка обработки файла: {str(e)}")

    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/upload/shr", response_model=Dict[str, Any])
async def upload_shr_messages(
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db)
):
    """
    Загрузка и обработка SHR телеграмм из текстовых файлов.
    Поддерживает форматы: JSON, XML, TXT
    """
    content = await file.read()
    content_str = content.decode('utf-8')

    parser = TelegramParser()
    geo_service = GeoService()

    processed = 0
    errors = []

    try:
        # Определяем формат файла
        if file.content_type == "application/json":
            try:
                data = json.loads(content_str)
                messages = data if isinstance(data, list) else [data]
            except:
                messages = content_str.split('\n')
        else:
            # Текстовый формат - каждая телеграмма на отдельной строке или блоке
            messages = content_str.split('\n\n') if '\n\n' in content_str else content_str.split('\n')

        for msg in messages:
            if not msg.strip() or 'SHR' not in msg:
                continue
                
            try:
                parsed = parser.parse_shr_message(msg)

                # Геопривязка
                dep_region = None
                arr_region = None
                
                if parsed['dep_coords']:
                    dep_region = geo_service.get_region_by_coordinates(
                        parsed['dep_coords'][0],
                        parsed['dep_coords'][1]
                    )

                if parsed['arr_coords']:
                    arr_region = geo_service.get_region_by_coordinates(
                        parsed['arr_coords'][0],
                        parsed['arr_coords'][1]
                    )

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
                    raw_shr=msg,
                    altitude_min=parsed.get('altitude', {}).get('min') if parsed.get('altitude') else None,
                    altitude_max=parsed.get('altitude', {}).get('max') if parsed.get('altitude') else None
                )

                db.add(flight)
                processed += 1

            except Exception as e:
                errors.append(f"Ошибка обработки телеграммы: {str(e)}")

        await db.commit()

        return {
            "processed": processed,
            "errors": errors[:10] if errors else [],
            "status": "success" if processed > 0 else "failed",
            "message": f"Обработано {processed} телеграмм из файла {file.filename}"
        }
        
    except Exception as e:
        raise HTTPException(500, f"Ошибка обработки файла: {str(e)}")


@router.get("/statistics", response_model=Dict[str, Any])
async def get_flight_statistics(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: AsyncSession = Depends(get_db)
):
    """Получение статистики по полетам за период"""
    query = select(Flight)
    
    if start_date:
        query = query.where(Flight.flight_date >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.where(Flight.flight_date <= datetime.combine(end_date, datetime.max.time()))
    
    result = await db.execute(query)
    flights = result.scalars().all()
    
    if not flights:
        return {
            "total_flights": 0,
            "avg_duration_minutes": 0,
            "unique_operators": 0,
            "unique_uav_types": 0,
            "period_start": start_date,
            "period_end": end_date
        }
    
    total_duration = sum(f.duration_minutes or 0 for f in flights)
    unique_operators = len(set(f.operator for f in flights if f.operator))
    unique_uav_types = len(set(f.uav_type for f in flights if f.uav_type))
    
    return {
        "total_flights": len(flights),
        "avg_duration_minutes": total_duration / len(flights) if flights else 0,
        "unique_operators": unique_operators,
        "unique_uav_types": unique_uav_types,
        "period_start": start_date,
        "period_end": end_date
    }


@router.get("/", response_model=List[Dict[str, Any]])
async def get_flights(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        region: Optional[str] = None,
        limit: int = Query(100, le=1000),
        offset: int = 0,
        db: AsyncSession = Depends(get_db)
):
    """Получение списка полетов с фильтрацией"""
    query = select(Flight)
    
    if start_date:
        query = query.where(Flight.flight_date >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.where(Flight.flight_date <= datetime.combine(end_date, datetime.max.time()))
    if region:
        query = query.where(
            (Flight.dep_region == region) | (Flight.arr_region == region)
        )
    
    query = query.order_by(Flight.flight_date.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    flights = result.scalars().all()
    
    return [
        {
            "id": f.id,
            "sid": f.sid,
            "flight_date": f.flight_date,
            "dep_region": f.dep_region,
            "arr_region": f.arr_region,
            "operator": f.operator,
            "uav_type": f.uav_type,
            "duration_minutes": f.duration_minutes,
            "status": f.status
        }
        for f in flights
    ]