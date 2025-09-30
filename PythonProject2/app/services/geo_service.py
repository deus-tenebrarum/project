from shapely.geometry import Point
from shapely.ops import transform
import json
import logging
from typing import Optional, Tuple, Dict
import httpx
from functools import lru_cache

logger = logging.getLogger(__name__)


class GeoService:
    """Сервис геопривязки к регионам РФ"""

    def __init__(self):
        self.regions_data = self._load_regions()

    def _load_regions(self) -> Dict:
        """Загрузка границ регионов из шейп-файлов или API"""
        # В продакшене здесь должна быть загрузка из PostGIS с актуальными границами
        # Пример структуры для демонстрации
        regions = {
            "Санкт-Петербург": {
                "code": "78",
                "bounds": [[59.5, 29.5], [60.5, 31.0]]  # Упрощенные границы
            },
            "Ленинградская область": {
                "code": "47",
                "bounds": [[58.5, 27.5], [61.5, 35.5]]
            },
            "Москва": {
                "code": "77",
                "bounds": [[55.1, 36.8], [56.0, 38.0]]
            },
            "Московская область": {
                "code": "50",
                "bounds": [[54.2, 35.1], [57.0, 40.2]]
            },
            "Мурманская область": {
                "code": "51",
                "bounds": [[66.0, 28.0], [70.0, 42.0]]
            },
            "Красноярский край": {
                "code": "24",
                "bounds": [[51.0, 84.0], [77.0, 114.0]]
            },
            "Новосибирская область": {
                "code": "54",
                "bounds": [[53.0, 75.0], [56.5, 85.5]]
            },
            "Ростовская область": {
                "code": "61",
                "bounds": [[46.0, 38.0], [50.5, 44.0]]
            },
            "Свердловская область": {
                "code": "66",
                "bounds": [[56.0, 57.0], [62.0, 66.5]]
            },
            "Тюменская область": {
                "code": "72",
                "bounds": [[55.0, 65.0], [73.5, 85.0]]
            }
        }
        return regions

    @lru_cache(maxsize=1000)
    def get_region_by_coordinates(self, lat: float, lon: float) -> Optional[str]:
        """
        Определение региона по координатам
        В продакшене использовать PostGIS ST_Contains
        """
        point = Point(lon, lat)

        # Упрощенная логика для демонстрации
        # В реальности нужно использовать точные полигоны границ
        for region_name, region_data in self.regions_data.items():
            bounds = region_data["bounds"]
            if (bounds[0][0] <= lat <= bounds[1][0] and
                    bounds[0][1] <= lon <= bounds[1][1]):
                return region_name

        return "Неопределен"

    def calculate_distance(self, coord1: Tuple[float, float],
                           coord2: Tuple[float, float]) -> float:
        """Расчет расстояния между координатами в километрах"""
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Радиус Земли в километрах

        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c