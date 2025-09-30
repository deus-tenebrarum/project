from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
import json

from app.core.database import get_db
from app.models.flight import Flight
from app.services.parser import TelegramParser
from app.services.geo_service import GeoService
from app.services.excel_parser import ExcelParser
from app.services.shr_parser import SHRDataParser
from app.schemas.flight import FlightCreate, FlightResponse, FlightStatistics

router = APIRouter()


@router.post("/upload/shr", response_model=Dict[str, Any])
async def upload_shr_messages(
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db)
):
    """Загрузка и обработка SHR телеграмм"""
    content = await file.read()
    content_str = content.decode('utf-8')

    parser = TelegramParser()
    shr_parser = SHRDataParser()
    geo_service = GeoService()

    processed = 0
    errors = []

    # Определяем формат файла
    if file.content_type == "application/json":
        try:
            data = json.loads(content_str)
            # Обработка JSON формата
            messages = data if isinstance(data, list) else [data]
        except:
            messages = content_str.split('\n')
    else:
        # Проверяем, это табличный формат или обычные телеграммы
        if '\t' in content_str and any(center in content_str for center in
                                       ['Санкт-Петербургский', 'Ростовский', 'Московский']):
            # Табличный формат из документа
            flights_data = shr_parser.parse_shr_document(content_str)

            for flight_data in flights_data:
                try:
                    # Геопривязка
                    dep_region = None
                    arr_region = None

                    if flight_data.get('dep_coords'):
                        coords = flight_data['dep_coords']
                        if isinstance(coords, tuple):
                            dep_region = geo_service.get_region_by_coordinates(coords[0], coords[1])

                    if flight_data.get('arr_coords'):
                        coords = flight_data['arr_coords']
                        if isinstance(coords, tuple):
                            arr_region = geo_service.get_region_by_coordinates(coords[0], coords[1])

                    # Создание записи в БД
                    flight = Flight(
                        sid=flight_data.get('sid'),
                        flight_date=flight_data.get('date'),
                        dep_time=flight_data.get('dep_time'),
                        arr_time=flight_data.get('arr_time'),
                        dep_coords=str(flight_data['dep_coords']) if flight_data.get('dep_coords') else None,
                        arr_coords=str(flight_data['arr_coords']) if flight_data.get('arr_coords') else None,
                        dep_region=dep_region,
                        arr_region=arr_region,
                        operator=flight_data.get('operator'),
                        uav_type=flight_data.get('uav_type'),
                        uav_reg=flight_data.get('registration'),
                        duration_minutes=flight_data.get('duration_minutes'),
                        center_name=flight_data.get('center_name'),
                        raw_shr=flight_data.get('raw_shr'),
                        raw_dep=flight_data.get('raw_dep'),
                        raw_arr=flight_data.get('raw_arr'),
                        altitude_min=flight_data.get('altitude', {}).get('min') if flight_data.get(
                            'altitude') else None,
                        altitude_max=flight_data.get('altitude', {}).get('max') if flight_data.get('altitude') else None
                    )

                    db.add(flight)
                    processed += 1

                except Exception as e:
                    errors.append(f"Ошибка обработки записи: {str(e)}")
        else:
            # Обычные SHR телеграммы
            messages = content_str.split('\n')

            for msg in messages:
                if 'SHR-' in msg:
                    try:
                        parsed = parser.parse_shr_message(msg)

                        # Геопривязка
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
                        errors.append(f"Ошибка обработки: {str(e)}")

    await db.commit()

    return {
        "processed": processed,
        "errors": errors[:10] if errors else [],  # Ограничиваем количество ошибок в ответе
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
        errors = []

        for flight_data in flights_data:
            try:
                # Геопривязка
                dep_region = None
                arr_region = None

                if flight_data.get('dep_coords_parsed'):
                    dep_region = geo_service.get_region_by_coordinates(
                        flight_data['dep_coords_parsed'][0],
                        flight_data['dep_coords_parsed'][1]
                    )

                if flight_data.get('arr_coords_parsed'):
                    arr_region = geo_service.get_region_by_coordinates(
                        flight_data['arr_coords_parsed'][0],
                        flight_data['arr_coords_parsed'][1]
                    )

                # Создание записи в БД с полными данными
                flight = Flight(
                    flight_date=flight_data.get('date'),
                    dep_time=flight_data.get('dep_time'),
                    arr_time=flight_data.get('arr_time'),
                    dep_coords=flight_data.get('dep_coords'),
                    arr_coords=flight_data.get('arr_coords'),
                    dep_region=dep_region,
                    arr_region=arr_region,
                    uav_type=flight_data.get('aircraft_type'),
                    uav_reg=flight_data.get('aircraft'),
                    duration_minutes=flight_data.get('duration_minutes'),
                    operator=flight_data.get('operator'),
                    operator_phone=flight_data.get('operator_phone'),
                    flight_zone={"route": flight_data.get('route')} if flight_data.get('route') else None,
                    status='arrived' if flight_data.get('arr_time') else 'scheduled'
                )

                db.add(flight)
                processed += 1

            except Exception as e:
                errors.append(f"Ошибка обработки записи: {str(e)}")

        await db.commit()

    except Exception as e:
        raise HTTPException(500, f"Ошибка обработки файла: {str(e)}")

    finally:
        os.unlink(tmp_path)

    return {
        "processed": processed,
        "errors": errors[:10] if errors else [],
        "status": "success" if processed > 0 else "failed"
    }
