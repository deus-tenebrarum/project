from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Literal

class ReportRequest(BaseModel):
    format: Literal["json", "png", "xlsx"]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    regions: Optional[List[str]] = None
    chart_type: Optional[Literal["bar", "pie", "line"]] = "bar"

class ReportResponse(BaseModel):
    status: str
    file_path: str
    format: str
    size_bytes: int