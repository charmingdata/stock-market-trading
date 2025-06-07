from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class FinancialStatementItems(BaseModel):
    """Financial statement data extracted from SEC filings."""
    cik: str
    company_name: str
    form_type: str
    filing_date: datetime
    document_url: str
    fiscal_year: int
    
    # Financial metrics as strings (will be converted to numbers for analysis)
    revenue: Optional[str] = None
    operating_income: Optional[str] = None
    net_income: Optional[str] = None
    eps_basic: Optional[str] = None
    eps_diluted: Optional[str] = None
    cash_and_equivalents: Optional[str] = None
    
    # Additional metadata
    quarter: Optional[str] = None