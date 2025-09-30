import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ExcelParser:
    """Парсер Excel файлов с полетными данными"""

    @staticmethod
    def parse_flight_data(file_path: str) -> List[Dict[str, Any]]:
        """Парсинг Excel файла с данными о полетах"""
        try:
            df = pd.read_excel(file_path, engine='openpyxl')

            flights = []
            for _, row in df.iterrows():
                flight = {
                    'date': pd.to_datetime(row.get('Дата')),
                    'flight_number': row.get('Рейс'),
                    'aircraft': row.get('Борт'),
                    'aircraft_type': row.get('Тип ВС'),
                    'dep_time': row.get('Т выл.факт'),
                    'arr_time': row.get('Т пос.факт'),
                    'dep_coords': row.get('АРВ'),
                    'dep_airport': row.get('А/В'),
                    'arr_coords': row.get('АРП'),
                    'arr_airport': row.get('А/П'),
                    'route': row.get('Маршрут'),
                    'field_18': row.get('Поле 18')
                }

                # Парсинг координат из строк
                if flight['dep_coords'] and isinstance(flight['dep_coords'], str):
                    from app.services.parser import TelegramParser
                    coords = TelegramParser.parse_coordinates(flight['dep_coords'])
                    flight['dep_coords_parsed'] = coords

                if flight['arr_coords'] and isinstance(flight['arr_coords'], str):
                    from app.services.parser import TelegramParser
                    coords = TelegramParser.parse_coordinates(flight['arr_coords'])
                    flight['arr_coords_parsed'] = coords

                flights.append(flight)

            logger.info(f"Успешно распарсено {len(flights)} полетов из Excel")
            return flights

        except Exception as e:
            logger.error(f"Ошибка парсинга Excel файла: {e}")
            raise