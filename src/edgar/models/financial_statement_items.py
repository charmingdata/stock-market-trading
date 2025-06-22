from datetime import datetime
from typing import Optional
from pydantic import BaseModel, model_validator
from ..search.company_mapping import get_standardized_company_name

class FinancialStatementItems(BaseModel):
    """Financial statement data extracted from SEC filings."""
    cik: str
    company_name: Optional[str] = None
    form_type: str
    filing_date: datetime
    document_url: str
    fiscal_year: int
    fiscal_quarter: Optional[int] = None
    
    @classmethod
    def set_company_name(cls, values):
        # values is a dict of all input data
        cik = values.get("cik")
        if not values.get("company_name") and cik:
            values["company_name"] = get_standardized_company_name(cik)
        return values
    
class IncomeStatementItems(FinancialStatementItems):
    """Income statement data extracted from SEC filings."""
    revenue: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    # No EPS here (see below)

class BalanceSheetItems(FinancialStatementItems):
    """Balance sheet data extracted from SEC filings."""
    total_assets: Optional[float] = None
    total_equity: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    # TODO: Add more balance sheet specific fields

class CashFlowItems(FinancialStatementItems):
    """Cash flow data extracted from SEC filings."""
    operating_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None
    # TODO: Add cash flow specific fields
    
class FinancialRatios(BaseModel):
    cik: str
    fiscal_year: int
    fiscal_quarter: Optional[int] = None
    eps_basic: Optional[float] = None
    eps_diluted: Optional[float] = None
    # Add other ratios as needed