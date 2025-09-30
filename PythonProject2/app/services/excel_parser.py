import pandas as pd
from datetime import datetime, time
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class ExcelParser:
    """Парсер Excel файлов с полетными данными"""

    @staticmethod
    def parse_time_string(time_str) -> datetime:
        """Парсинг строки времени в datetime"""
        if pd.isna(time_str) or not time_str:
            return None

        if isinstance(time_str, str):
            # Пробуем разные форматы
            formats = [
                '%H:%M:%S',
                '%H:%M',
                '%I:%M %p',
                '%I:%M:%S %p'
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(time_str, fmt).time()
                except:
                    continue
        elif isinstance(time_str, (datetime, pd.Timestamp)):
            return time_str.time()
        elif isinstance(time_str, time):
            return time_str

        return None

    @staticmethod
    def parse_date_field(date_val) -> datetime:
        """Парсинг даты из разных форматов"""
        if pd.isna(date_val):
            return None

        if isinstance(date_val, (datetime, pd.Timestamp)):
            return date_val

        if isinstance(date_val, str):
            # Пробуем разные форматы дат
            formats = [
                '%d/%m/%y',
                '%d/%m/%Y',
                '%Y-%m-%d',
                '%d.%m.%Y',
                '%d.%m.%y'
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_val, fmt)
                except:
                    continue

        return pd.to_datetime(date_val, errors='coerce')

    @staticmethod
    def parse_flight_data(file_path: str) -> List[Dict[str, Any]]:
        """Парсинг Excel файла с данными о полетах"""
        try:
            # Читаем Excel с правильными настройками
            df = pd.read_excel(
                file_path,
                engine='openpyxl',
                parse_dates=False,  # Отключаем автопарсинг дат
                dtype=str  # Читаем все как строки для контроля
            )

            logger.info(f"Загружено {len(df)} строк из Excel")
            logger.info(f"Колонки: {df.columns.tolist()}")

            flights = []

            for idx, row in df.iterrows():
                try:
                    # Парсим дату
                    flight_date = ExcelParser.parse_date_field(row.get('Дата'))

                    # Парсим время вылета и посадки
                    dep_time_str = row.get('Т выл.факт')
                    arr_time_str = row.get('Т пос.факт')

                    dep_time_obj = ExcelParser.parse_time_string(dep_time_str)
                    arr_time_obj = ExcelParser.parse_time_string(arr_time_str)

                    # Создаем полные datetime объекты
                    dep_datetime = None
                    arr_datetime = None

                    if flight_date and dep_time_obj:
                        dep_datetime = datetime.combine(flight_date.date(), dep_time_obj)

                    if flight_date and arr_time_obj:
                        arr_datetime = datetime.combine(flight_date.date(), arr_time_obj)

                    # Рассчитываем продолжительность
                    duration_minutes = None
                    if dep_datetime and arr_datetime:
                        duration = arr_datetime - dep_datetime
                        # Если прилет на следующий день
                        if duration.total_seconds() < 0:
                            arr_datetime += pd.Timedelta(days=1)
                            duration = arr_datetime - dep_datetime
                        duration_minutes = int(duration.total_seconds() / 60)

                    # Парсим координаты
                    dep_coords = row.get('АРВ')
                    arr_coords = row.get('АРП')

                    dep_coords_parsed = None
                    arr_coords_parsed = None

                    if dep_coords and isinstance(dep_coords, str):
                        from app.services.parser import TelegramParser
                        dep_coords_parsed = TelegramParser.parse_coordinates(dep_coords)

                    if arr_coords and isinstance(arr_coords, str):
                        from app.services.parser import TelegramParser
                        arr_coords_parsed = TelegramParser.parse_coordinates(arr_coords)

                    # Обрабатываем поле 18 для извлечения дополнительной информации
                    field_18 = row.get('Поле 18', '')
                    operator = None
                    operator_phone = None

                    if field_18:
                        # Ищем оператора
                        opr_match = re.search(r'OPR/([^/]+)', str(field_18))
                        if opr_match:
                            operator = opr_match.group(1).strip()

                        # Ищем телефон
                        phone_match = re.search(r'\+?[78][\d\s\-\(\)]{10,}', str(field_18))
                        if phone_match:
                            operator_phone = phone_match.group(0).strip()

                    flight = {
                        'date': flight_date,
                        'flight_number': row.get('Рейс'),
                        'aircraft': row.get('Борт'),
                        'aircraft_type': row.get('Тип ВС'),
                        'dep_time': dep_datetime,
                        'arr_time': arr_datetime,
                        'dep_coords': dep_coords,
                        'dep_airport': row.get('А/В'),
                        'arr_coords': arr_coords,
                        'arr_airport': row.get('А/П'),
                        'route': row.get('Маршрут'),
                        'field_18': field_18,
                        'dep_coords_parsed': dep_coords_parsed,
                        'arr_coords_parsed': arr_coords_parsed,
                        'duration_minutes': duration_minutes,
                        'operator': operator,
                        'operator_phone': operator_phone
                    }

                    flights.append(flight)

                except Exception as e:
                    logger.warning(f"Ошибка парсинга строки {idx}: {e}")
                    continue

            logger.info(f"Успешно распарсено {len(flights)} полетов из Excel")
            return flights

        except Exception as e:
            logger.error(f"Ошибка парсинга Excel файла: {e}")
            raise