import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import tempfile
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.flight import Flight


class ReportGenerator:
    """Генератор отчетов и визуализаций"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def generate_json_report(
            self,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            regions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Генерация JSON отчета"""

        query = select(Flight)

        if start_date:
            query = query.where(Flight.flight_date >= start_date)
        if end_date:
            query = query.where(Flight.flight_date <= end_date)
        if regions:
            query = query.where(Flight.dep_region.in_(regions))

        result = await self.db.execute(query)
        flights = result.scalars().all()

        # Агрегация данных
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "period_start": start_date.isoformat() if start_date else None,
                "period_end": end_date.isoformat() if end_date else None,
                "total_records": len(flights)
            },
            "summary": {
                "total_flights": len(flights),
                "unique_operators": len(set(f.operator for f in flights if f.operator)),
                "unique_regions": len(set(f.dep_region for f in flights if f.dep_region)),
                "total_flight_hours": sum(f.duration_minutes or 0 for f in flights) / 60
            },
            "by_region": {},
            "by_operator": {},
            "by_uav_type": {},
            "daily_statistics": {}
        }

        # Группировка по регионам
        for flight in flights:
            region = flight.dep_region or "Неизвестный"
            if region not in report["by_region"]:
                report["by_region"][region] = {
                    "flights": 0,
                    "duration_minutes": 0,
                    "operators": set()
                }
            report["by_region"][region]["flights"] += 1
            report["by_region"][region]["duration_minutes"] += flight.duration_minutes or 0
            if flight.operator:
                report["by_region"][region]["operators"].add(flight.operator)

        # Преобразование set в list для JSON
        for region in report["by_region"]:
            report["by_region"][region]["operators"] = list(
                report["by_region"][region]["operators"]
            )

        return report

    async def generate_chart(
            self,
            chart_type: str = "bar",
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
    ) -> str:
        """Генерация графика в формате PNG"""

        # Получение данных для графика
        query = select(
            Flight.dep_region,
            func.count(Flight.id).label('count')
        ).group_by(Flight.dep_region)

        if start_date:
            query = query.where(Flight.flight_date >= start_date)
        if end_date:
            query = query.where(Flight.flight_date <= end_date)

        query = query.order_by(func.count(Flight.id).desc()).limit(10)

        result = await self.db.execute(query)
        data = result.all()

        # Создание графика
        plt.figure(figsize=(12, 6))
        plt.style.use('seaborn-v0_8-darkgrid')

        regions = [row.dep_region or "Неизвестный" for row in data]
        counts = [row.count for row in data]

        if chart_type == "bar":
            plt.bar(regions, counts, color='skyblue', edgecolor='navy')
            plt.xlabel('Регион')
            plt.ylabel('Количество полетов')
            plt.title('Топ-10 регионов по количеству полетов БАС')
            plt.xticks(rotation=45, ha='right')

        elif chart_type == "pie":
            plt.pie(counts, labels=regions, autopct='%1.1f%%', startangle=90)
            plt.title('Распределение полетов БАС по регионам')

        elif chart_type == "line":
            # Для линейного графика нужны временные данные
            query = select(
                func.date(Flight.flight_date).label('date'),
                func.count(Flight.id).label('count')
            ).group_by(func.date(Flight.flight_date))

            if start_date:
                query = query.where(Flight.flight_date >= start_date)
            if end_date:
                query = query.where(Flight.flight_date <= end_date)

            query = query.order_by(func.date(Flight.flight_date))

            result = await self.db.execute(query)
            time_data = result.all()

            dates = [row.date for row in time_data]
            counts = [row.count for row in time_data]

            plt.plot(dates, counts, marker='o', linestyle='-', linewidth=2, markersize=6)
            plt.xlabel('Дата')
            plt.ylabel('Количество полетов')
            plt.title('Динамика полетов БАС')
            plt.xticks(rotation=45, ha='right')
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))

        plt.tight_layout()

        # Сохранение в временный файл
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            plt.savefig(f.name, dpi=300, bbox_inches='tight')
            plt.close()
            return f.name