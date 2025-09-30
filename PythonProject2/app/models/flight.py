from sqlalchemy import Column, String, DateTime, Float, Integer, JSON, Index, Text
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from datetime import datetime
from enum import Enum

Base = declarative_base()


class FlightStatus(str, Enum):
    SCHEDULED = "scheduled"
    DEPARTED = "departed"
    ARRIVED = "arrived"
    CANCELLED = "cancelled"


class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    sid = Column(String(20), unique=True, index=True)  # ID из SHR
    flight_date = Column(DateTime, index=True)

    # Данные о взлете/посадке
    dep_point = Column(Geometry('POINT', srid=4326))
    dep_coords = Column(String(50))
    dep_time = Column(DateTime)
    dep_region = Column(String(100), index=True)

    arr_point = Column(Geometry('POINT', srid=4326))
    arr_coords = Column(String(50))
    arr_time = Column(DateTime)
    arr_region = Column(String(100), index=True)

    # Информация о БВС
    uav_type = Column(String(50))
    uav_reg = Column(String(50))
    operator = Column(String(200))
    operator_phone = Column(String(20))

    # Полетные данные
    altitude_min = Column(Float)
    altitude_max = Column(Float)
    flight_zone = Column(JSON)
    duration_minutes = Column(Integer)

    # Служебная информация
    status = Column(String(20), default=FlightStatus.SCHEDULED)
    center_name = Column(String(100))  # Центр ЕС ОрВД
    raw_shr = Column(Text)
    raw_dep = Column(Text)
    raw_arr = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_flight_date_region', 'flight_date', 'dep_region'),
        Index('idx_operator', 'operator'),
    )