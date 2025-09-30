import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SHRDataParser:
    """Парсер данных из документов с SHR телеграммами"""

    @staticmethod
    def parse_shr_document(content: str) -> List[Dict]:
        """Парсинг документа с SHR телеграммами в табличном формате"""
        flights = []
        lines = content.strip().split('\n')

        current_center = None
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Определяем центр ЕС ОрВД
            if any(center in line for center in ['Санкт-Петербургский', 'Ростовский', 'Новосибирский',
                                                 'Екатеринбургский', 'Московский', 'Красноярский', 'Тюменский']):
                current_center = line.split('\t')[0] if '\t' in line else line
                i += 1
                continue

            # Парсим данные полета
            if '\t' in line and current_center:
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        shr_data = parts[1] if len(parts) > 1 else ""
                        dep_data = parts[2] if len(parts) > 2 else ""
                        arr_data = parts[3] if len(parts) > 3 else ""

                        flight_info = SHRDataParser.parse_combined_data(
                            shr_data, dep_data, arr_data, current_center
                        )

                        if flight_info:
                            flights.append(flight_info)

                    except Exception as e:
                        logger.warning(f"Ошибка парсинга строки: {e}")

            i += 1

        return flights

    @staticmethod
    def parse_combined_data(shr_text: str, dep_text: str, arr_text: str, center: str) -> Optional[Dict]:
        """Комбинированный парсинг SHR, DEP и ARR данных"""
        from app.services.parser import TelegramParser

        result = {
            'center_name': center,
            'raw_shr': shr_text,
            'raw_dep': dep_text,
            'raw_arr': arr_text
        }

        # Парсим SHR
        if shr_text:
            shr_data = TelegramParser.parse_shr_message(shr_text)
            result.update(shr_data)

        # Парсим DEP
        if dep_text and 'TITLE IDEP' in dep_text:
            dep_data = TelegramParser.parse_dep_message(dep_text)

            # Обновляем времена вылета
            if dep_data.get('atd') and dep_data.get('add'):
                try:
                    date_str = dep_data['add']
                    time_str = dep_data['atd']

                    year = 2000 + int(date_str[0:2])
                    month = int(date_str[2:4])
                    day = int(date_str[4:6])
                    hour = int(time_str[0:2])
                    minute = int(time_str[2:4])

                    result['dep_time'] = datetime(year, month, day, hour, minute)
                except:
                    pass

            if dep_data.get('adepz'):
                result['dep_coords'] = dep_data['adepz']

        # Парсим ARR
        if arr_text and 'TITLE IARR' in arr_text:
            arr_data = TelegramParser.parse_arr_message(arr_text)

            # Обновляем времена прилета
            if arr_data.get('ata') and arr_data.get('ada'):
                try:
                    date_str = arr_data['ada']
                    time_str = arr_data['ata']

                    year = 2000 + int(date_str[0:2])
                    month = int(date_str[2:4])
                    day = int(date_str[4:6])
                    hour = int(time_str[0:2])
                    minute = int(time_str[2:4])

                    result['arr_time'] = datetime(year, month, day, hour, minute)
                except:
                    pass

            if arr_data.get('adarrz'):
                result['arr_coords'] = arr_data['adarrz']

        # Рассчитываем продолжительность
        if result.get('dep_time') and result.get('arr_time'):
            duration = result['arr_time'] - result['dep_time']
            result['duration_minutes'] = int(duration.total_seconds() / 60)

        return result