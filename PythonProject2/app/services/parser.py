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
        Парсинг координат из формата DDMMN/DDDMME или DDMMSN/DDDMMSE
        Примеры: 
        - 5957N02905E -> (59.95, 29.083)
        - 440846N0430829E -> (44.1461, 43.1414)
        """
        if not coord_str:
            return None
        
        # Убираем пробелы и переносы строк
        coord_str = coord_str.strip().replace(' ', '').replace('\r', '').replace('\n', '')
        
        # Паттерн 1: DDMMN/DDDMME (стандартный)
        pattern1 = r'(\d{2})(\d{2})([NS])(\d{3})(\d{2})([EW])'
        match = re.match(pattern1, coord_str)
        
        if match:
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
        
        # Паттерн 2: DDMMSN/DDDMMSE (с секундами)
        pattern2 = r'(\d{2})(\d{2})(\d{2})([NS])(\d{3})(\d{2})(\d{2})([EW])'
        match = re.match(pattern2, coord_str)
        
        if match:
            lat_deg = int(match.group(1))
            lat_min = int(match.group(2))
            lat_sec = int(match.group(3))
            lat_dir = match.group(4)
            
            lon_deg = int(match.group(5))
            lon_min = int(match.group(6))
            lon_sec = int(match.group(7))
            lon_dir = match.group(8)
            
            lat = lat_deg + lat_min / 60.0 + lat_sec / 3600.0
            if lat_dir == 'S':
                lat = -lat
            
            lon = lon_deg + lon_min / 60.0 + lon_sec / 3600.0
            if lon_dir == 'W':
                lon = -lon
            
            return (lat, lon)
        
        logger.debug(f"Не удалось распарсить координаты: {coord_str}")
        return None

    @staticmethod
    def parse_shr_message(shr_text: str) -> Dict:
        """
        Парсинг SHR телеграммы
        Пример: (SHR-ZZZZZ -ZZZZ0900 -M0016/M0026 /ZONA R0,7 5509N03737E/ 
                 -DEP/5509N03737E DEST/5509N03737E DOF/240101 OPR/ОПЕРАТОР...)
        """
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
        
        # Очистка текста от лишних переносов и пробелов
        shr_text = re.sub(r'\s+', ' ', shr_text.replace('\r\n', ' ').replace('\n', ' '))
        
        # Извлечение SID
        sid_match = re.search(r'SID[/\s]+([A-Z0-9]+)', shr_text, re.IGNORECASE)
        if sid_match:
            result['sid'] = sid_match.group(1).strip()
        
        # Извлечение координат вылета
        dep_patterns = [
            r'DEP/(\d{4,6}[NS]\d{5,7}[EW])',  # DEP/координаты
            r'ADEPZ\s+(\d{4,6}[NS]\d{5,7}[EW])',  # ADEPZ координаты
        ]
        for pattern in dep_patterns:
            dep_match = re.search(pattern, shr_text, re.IGNORECASE)
            if dep_match:
                coords = TelegramParser.parse_coordinates(dep_match.group(1))
                if coords:
                    result['dep_coords'] = coords
                    break
        
        # Извлечение координат прилета
        dest_patterns = [
            r'DEST/(\d{4,6}[NS]\d{5,7}[EW])',  # DEST/координаты
            r'ADARRZ\s+(\d{4,6}[NS]\d{5,7}[EW])',  # ADARRZ координаты
        ]
        for pattern in dest_patterns:
            dest_match = re.search(pattern, shr_text, re.IGNORECASE)
            if dest_match:
                coords = TelegramParser.parse_coordinates(dest_match.group(1))
                if coords:
                    result['arr_coords'] = coords
                    break
        
        # Извлечение даты DOF/YYMMDD
        dof_match = re.search(r'DOF/(\d{6})', shr_text)
        if dof_match:
            date_str = dof_match.group(1)
            try:
                year = 2000 + int(date_str[0:2])
                month = int(date_str[2:4])
                day = int(date_str[4:6])
                result['date'] = datetime(year, month, day)
            except Exception as e:
                logger.debug(f"Ошибка парсинга даты DOF: {e}")
        
        # Извлечение оператора
        # Паттерны: OPR/текст до следующего поля или конца
        opr_match = re.search(r'OPR/([^/\r\n]+?)(?:\s+(?:REG|TYP|RMK|STS|SID|EET|DOF|DEST|DEP|[\+\d])|$)', shr_text, re.IGNORECASE)
        if opr_match:
            operator = opr_match.group(1).strip()
            # Убираем телефоны из имени оператора
            operator = re.sub(r'\+?\d[\d\s\-\(\)]{9,}', '', operator).strip()
            result['operator'] = operator
        
        # Извлечение типа БВС
        typ_match = re.search(r'TYP/(\w+)', shr_text, re.IGNORECASE)
        if typ_match:
            result['uav_type'] = typ_match.group(1).strip()
        
        # Извлечение регистрации
        reg_patterns = [
            r'REG/([A-Z0-9]+)',  # REG/номер
            r'REG\s+([A-Z0-9]+)',  # REG номер
        ]
        for pattern in reg_patterns:
            reg_match = re.search(pattern, shr_text, re.IGNORECASE)
            if reg_match:
                result['registration'] = reg_match.group(1).strip()
                break
        
        # Извлечение высоты M0000/M0100
        alt_match = re.search(r'[/-]M(\d{4})/M(\d{4})', shr_text)
        if alt_match:
            try:
                min_alt = int(alt_match.group(1))
                max_alt = int(alt_match.group(2))
                result['altitude'] = {
                    'min': min_alt,
                    'max': max_alt
                }
            except:
                pass
        
        # Извлечение зоны полета
        zone_match = re.search(r'ZONA\s+([^/]+?)(?:/|$)', shr_text, re.IGNORECASE)
        if zone_match:
            result['zone'] = zone_match.group(1).strip()
        
        return result

    @staticmethod
    def parse_dep_message(dep_text: str) -> Dict:
        """
        Парсинг DEP телеграммы (вылет)
        Пример: (DEP-ZZZZZ-ZZZZ0900-ZZZZ -REG/07C4935 DOF/240101...)
        """
        result = {
            'type': 'DEP',
            'sid': None,
            'add': None,  # Actual Date of Departure
            'atd': None,  # Actual Time of Departure
            'adep': None,  # Aerodrome of Departure
            'adepz': None,  # Departure coordinates
            'registration': None
        }
        
        # Очистка текста
        dep_text = re.sub(r'\s+', ' ', dep_text.replace('\r\n', ' ').replace('\n', ' '))
        
        # SID
        sid_patterns = [
            r'SID[/\s]+([A-Z0-9]+)',
            r'-SID\s+(\d+)',
        ]
        for pattern in sid_patterns:
            sid_match = re.search(pattern, dep_text, re.IGNORECASE)
            if sid_match:
                result['sid'] = sid_match.group(1).strip()
                break
        
        # ADD - дата вылета
        add_match = re.search(r'ADD\s+(\d{6})', dep_text, re.IGNORECASE)
        if add_match:
            result['add'] = add_match.group(1)
        else:
            # Альтернатива: DOF
            dof_match = re.search(r'DOF/(\d{6})', dep_text)
            if dof_match:
                result['add'] = dof_match.group(1)
        
        # ATD - время вылета
        atd_match = re.search(r'ATD\s+(\d{4})', dep_text, re.IGNORECASE)
        if atd_match:
            result['atd'] = atd_match.group(1)
        
        # ADEPZ - координаты вылета
        adepz_match = re.search(r'ADEPZ\s+(\d{4,6}[NS]\d{5,7}[EW])', dep_text, re.IGNORECASE)
        if adepz_match:
            coords = TelegramParser.parse_coordinates(adepz_match.group(1))
            if coords:
                result['adepz'] = coords
        else:
            # Альтернатива: DEP/координаты
            dep_coords_match = re.search(r'DEP/(\d{4,6}[NS]\d{5,7}[EW])', dep_text)
            if dep_coords_match:
                coords = TelegramParser.parse_coordinates(dep_coords_match.group(1))
                if coords:
                    result['adepz'] = coords
        
        # REG - регистрация
        reg_match = re.search(r'REG[/\s]+([A-Z0-9]+)', dep_text, re.IGNORECASE)
        if reg_match:
            result['registration'] = reg_match.group(1).strip()
        
        return result

    @staticmethod
    def parse_arr_message(arr_text: str) -> Dict:
        """
        Парсинг ARR телеграммы (прилет)
        Пример: (ARR-ZZZZZ-ZZZZ0900-ZZZZ1515 -REG/07C4935 DOF/240101...)
        """
        result = {
            'type': 'ARR',
            'sid': None,
            'ada': None,  # Actual Date of Arrival
            'ata': None,  # Actual Time of Arrival
            'adarr': None,  # Aerodrome of Arrival
            'adarrz': None,  # Arrival coordinates
            'registration': None
        }
        
        # Очистка текста
        arr_text = re.sub(r'\s+', ' ', arr_text.replace('\r\n', ' ').replace('\n', ' '))
        
        # SID
        sid_patterns = [
            r'SID[/\s]+([A-Z0-9]+)',
            r'-SID\s+(\d+)',
        ]
        for pattern in sid_patterns:
            sid_match = re.search(pattern, arr_text, re.IGNORECASE)
            if sid_match:
                result['sid'] = sid_match.group(1).strip()
                break
        
        # ADA - дата прилета
        ada_match = re.search(r'ADA\s+(\d{6})', arr_text, re.IGNORECASE)
        if ada_match:
            result['ada'] = ada_match.group(1)
        else:
            # Альтернатива: DOF
            dof_match = re.search(r'DOF/(\d{6})', arr_text)
            if dof_match:
                result['ada'] = dof_match.group(1)
        
        # ATA - время прилета
        ata_match = re.search(r'ATA\s+(\d{4})', arr_text, re.IGNORECASE)
        if ata_match:
            result['ata'] = ata_match.group(1)
        
        # ADARRZ - координаты прилета
        adarrz_match = re.search(r'ADARRZ\s+(\d{4,6}[NS]\d{5,7}[EW])', arr_text, re.IGNORECASE)
        if adarrz_match:
            coords = TelegramParser.parse_coordinates(adarrz_match.group(1))
            if coords:
                result['adarrz'] = coords
        else:
            # Альтернатива: DEST/координаты
            dest_coords_match = re.search(r'DEST/(\d{4,6}[NS]\d{5,7}[EW])', arr_text)
            if dest_coords_match:
                coords = TelegramParser.parse_coordinates(dest_coords_match.group(1))
                if coords:
                    result['adarrz'] = coords
        
        # REG - регистрация
        reg_match = re.search(r'REG[/\s]+([A-Z0-9]+)', arr_text, re.IGNORECASE)
        if reg_match:
            result['registration'] = reg_match.group(1).strip()
        
        return result

    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """Извлечение телефона из текста"""
        phone_match = re.search(r'\+?[78][\d\s\-\(\)]{10,}', text)
        if phone_match:
            return phone_match.group(0).strip()
        return None