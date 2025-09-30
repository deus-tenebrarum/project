import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TelegramParser:
    """Парсер формализованных телеграмм по приказу Минтранса №13"""

    @staticmethod
    def parse_coordinates(coord_str: str) -> Optional[Tuple[float, float]]:
        """
        Парсинг координат из формата DDMMN/DDDMME
        Пример: 5957N02905E -> (59.95, 29.083)
        """
        pattern = r'(\d{2})(\d{2})([NS])(\d{3})(\d{2})([EW])'
        match = re.match(pattern, coord_str.strip())

        if not match:
            return None

        lat_deg = int(match.group(1))
        lat_min = int(match.group(2))
        lat_dir = match.group(3)

        lon_deg = int(match.group(4))
        lon_min = int(match.group(5))
        lon_dir = match.group(6)

        lat = lat_deg + lat_min / 60.0
        if lat_dir == 'S':
            lat = -lat

        lon = lon_deg + lon_min / 60.0
        if lon_dir == 'W':
            lon = -lon

        return (lat, lon)

    @staticmethod
    def parse_shr_message(shr_text: str) -> Dict:
        """Парсинг SHR телеграммы"""
        result = {
            'type': 'SHR',
            'sid': None,
            'dep_coords': None,
            'arr_coords': None,
            'date': None,
            'operator': None,
            'uav_type': None,
            'registration': None,
            'altitude': None,
            'zone': None
        }

        # Извлечение SID
        sid_match = re.search(r'SID/(\d+)', shr_text)
        if sid_match:
            result['sid'] = sid_match.group(1)

        # Извлечение координат вылета/прилета
        dep_match = re.search(r'DEP/(\d{4}[NS]\d{5}[EW])', shr_text)
        if dep_match:
            coords = TelegramParser.parse_coordinates(dep_match.group(1))
            result['dep_coords'] = coords

        dest_match = re.search(r'DEST/(\d{4}[NS]\d{5}[EW])', shr_text)
        if dest_match:
            coords = TelegramParser.parse_coordinates(dest_match.group(1))
            result['arr_coords'] = coords

        # Извлечение даты
        dof_match = re.search(r'DOF/(\d{6})', shr_text)
        if dof_match:
            date_str = dof_match.group(1)
            year = 2000 + int(date_str[0:2])
            month = int(date_str[2:4])
            day = int(date_str[4:6])
            result['date'] = datetime(year, month, day)

        # Извлечение оператора
        opr_match = re.search(r'OPR/([^/\s]+(?:\s+[^/\s]+)*)', shr_text)
        if opr_match:
            result['operator'] = opr_match.group(1).strip()

        # Извлечение типа БВС
        typ_match = re.search(r'TYP/(\w+)', shr_text)
        if typ_match:
            result['uav_type'] = typ_match.group(1)

        # Извлечение регистрации
        reg_match = re.search(r'REG/([^/\s]+(?:\s+[^/\s]+)*)', shr_text)
        if reg_match:
            result['registration'] = reg_match.group(1).strip()

        # Извлечение высоты
        alt_match = re.search(r'M(\d{4})/M(\d{4})', shr_text)
        if alt_match:
            result['altitude'] = {
                'min': int(alt_match.group(1)),
                'max': int(alt_match.group(2))
            }

        return result

    @staticmethod
    def parse_dep_message(dep_text: str) -> Dict:
        """Парсинг DEP телеграммы (вылет)"""
        result = {
            'type': 'DEP',
            'sid': None,
            'add': None,  # Actual Date of Departure
            'atd': None,  # Actual Time of Departure
            'adep': None,  # Aerodrome of Departure
            'adepz': None,  # Departure coordinates
            'registration': None
        }

        sid_match = re.search(r'SID\s+(\d+)', dep_text)
        if sid_match:
            result['sid'] = sid_match.group(1)

        add_match = re.search(r'ADD\s+(\d{6})', dep_text)
        if add_match:
            result['add'] = add_match.group(1)

        atd_match = re.search(r'ATD\s+(\d{4})', dep_text)
        if atd_match:
            result['atd'] = atd_match.group(1)

        adepz_match = re.search(r'ADEPZ\s+(\d{4}[NS]\d{5}[EW])', dep_text)
        if adepz_match:
            coords = TelegramParser.parse_coordinates(adepz_match.group(1))
            result['adepz'] = coords

        reg_match = re.search(r'REG\s+([^\s]+)', dep_text)
        if reg_match:
            result['registration'] = reg_match.group(1)

        return result

    @staticmethod
    def parse_arr_message(arr_text: str) -> Dict:
        """Парсинг ARR телеграммы (прилет)"""
        result = {
            'type': 'ARR',
            'sid': None,
            'ada': None,  # Actual Date of Arrival
            'ata': None,  # Actual Time of Arrival
            'adarr': None,  # Aerodrome of Arrival
            'adarrz': None,  # Arrival coordinates
            'registration': None
        }

        sid_match = re.search(r'SID\s+(\d+)', arr_text)
        if sid_match:
            result['sid'] = sid_match.group(1)

        ada_match = re.search(r'ADA\s+(\d{6})', arr_text)
        if ada_match:
            result['ada'] = ada_match.group(1)

        ata_match = re.search(r'ATA\s+(\d{4})', arr_text)
        if ata_match:
            result['ata'] = ata_match.group(1)

        adarrz_match = re.search(r'ADARRZ\s+(\d{4}[NS]\d{5}[EW])', arr_text)
        if adarrz_match:
            coords = TelegramParser.parse_coordinates(adarrz_match.group(1))
            result['adarrz'] = coords

        reg_match = re.search(r'REG\s+([^\s]+)', arr_text)
        if reg_match:
            result['registration'] = reg_match.group(1)

        return result