from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class FlightBase(BaseModel):
    sid: Optional[str] = None
    flight_date: Optional[datetime] = None
    dep_coords: Optional[str] = None
    arr_coords: Optional[str] = None
    dep_region: Optional[str] = None
    arr_region: Optional[str] = None
    operator: Optional[str] = None
    uav_type: Optional[str] = None
    uav_reg: Optional[str] = None
    duration_minutes: Optional[int] = None


class FlightCreate(FlightBase):
    raw_shr: Optional[str] = None
    raw_dep: Optional[str] = None
    raw_arr: Optional[str] = None


class FlightResponse(FlightBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FlightStatistics(BaseModel):
    total_flights: int
    avg_duration_minutes: float
    unique_operators: int
    unique_uav_types: int
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None