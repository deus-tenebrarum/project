from pydantic import BaseModel
from typing import Optional

class RegionRating(BaseModel):
    position: int
    region: str
    flight_count: int
    total_duration_hours: float
    unique_operators: int

class RegionStatistics(BaseModel):
    region: str
    total_flights: int
    total_duration_hours: float
    unique_operators: int
    unique_uav_types: int
    peak_hour: int
    peak_hour_flights: int
    zero_flight_days: int
    avg_flights_per_day: float