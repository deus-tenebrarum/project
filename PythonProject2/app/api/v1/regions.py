from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.models.flight import Flight
from app.schemas.region import RegionStatistics, RegionRating

router = APIRouter()


@router.get("/rating", response_model=List[RegionRating])
async def get_regions_rating(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = Query(10, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    """Получение рейтинга регионов по количеству полетов"""
    query = select(
        Flight.dep_region.label('region'),
        func.count(Flight.id).label('flight_count'),
        func.sum(Flight.duration_minutes).label('total_duration'),
        func.count(func.distinct(Flight.operator)).label('unique_operators')
    ).group_by(Flight.dep_region)

    if start_date:
        query = query.where(Flight.flight_date >= start_date)
    if end_date:
        query = query.where(Flight.flight_date <= end_date)

    query = query.order_by(func.count(Flight.id).desc()).limit(limit)

    result = await db.execute(query)

    rating = []
    for idx, row in enumerate(result.all(), 1):
        if row.region:
            rating.append({
                "position": idx,
                "region": row.region,
                "flight_count": row.flight_count,
                "total_duration_hours": row.total_duration / 60 if row.total_duration else 0,
                "unique_operators": row.unique_operators
            })

    return rating


@router.get("/{region_name}/statistics", response_model=RegionStatistics)
async def get_region_statistics(
        region_name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: AsyncSession = Depends(get_db)
):
    """Получение детальной статистики по региону"""
    query = select(Flight).where(
        (Flight.dep_region == region_name) | (Flight.arr_region == region_name)
    )

    if start_date:
        query = query.where(Flight.flight_date >= start_date)
    if end_date:
        query = query.where(Flight.flight_date <= end_date)

    result = await db.execute(query)
    flights = result.scalars().all()

    # Расчет метрик
    total_flights = len(flights)
    total_duration = sum(f.duration_minutes or 0 for f in flights)
    unique_operators = len(set(f.operator for f in flights if f.operator))
    unique_uav_types = len(set(f.uav_type for f in flights if f.uav_type))

    # Расчет пиковых нагрузок
    flights_by_hour = {}
    for flight in flights:
        if flight.dep_time:
            hour = flight.dep_time.hour
            flights_by_hour[hour] = flights_by_hour.get(hour, 0) + 1

    peak_hour = max(flights_by_hour.items(), key=lambda x: x[1]) if flights_by_hour else (0, 0)

    # Подсчет дней без полетов
    if flights:
        flight_dates = set(f.flight_date.date() for f in flights if f.flight_date)
        if start_date and end_date:
            total_days = (end_date - start_date).days + 1
            zero_days = total_days - len(flight_dates)
        else:
            zero_days = 0
    else:
        zero_days = 0

    return {
        "region": region_name,
        "total_flights": total_flights,
        "total_duration_hours": total_duration / 60 if total_duration else 0,
        "unique_operators": unique_operators,
        "unique_uav_types": unique_uav_types,
        "peak_hour": peak_hour[0],
        "peak_hour_flights": peak_hour[1],
        "zero_flight_days": zero_days,
        "avg_flights_per_day": total_flights / max((end_date - start_date).days + 1,
                                                   1) if start_date and end_date else 0
    }
