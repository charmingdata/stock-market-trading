from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class SecFiling(BaseModel):
    """SEC Filing metadata."""
    cik: str
    company_name: str
    form_type: str
    filing_date: datetime
    document_url: str
    file_number: str
    fiscal_year: int
    submission_date: datetime
    fiscal_quarter: Optional[str] = None