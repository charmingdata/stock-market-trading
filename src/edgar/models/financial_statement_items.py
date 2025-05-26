"""Financial statement items extracted from SEC EDGAR filings.

This module defines Pydantic models for representing standardized financial metrics
from SEC EDGAR filings, focusing on key financial statement items that are:
- Consistently reported across filings
- Required by SEC regulations
- Essential for financial analysis

Key components:
- Income Statement: revenue, operating income, net income, EPS
- Balance Sheet: cash and equivalents
- Contextual Data: fiscal period, reporting dates

The models provide:
- Type validation for financial metrics
- Fiscal period validation (quarters, years)
- Integration with SEC filing metadata
- Support for both 10-K and 10-Q data points

Example:
    >>> items = FinancialStatementItems(
    ...     revenue="100000000",
    ...     operating_income="15000000",
    ...     net_income="10000000",
    ...     eps_basic="1.50",
    ...     eps_diluted="1.45",
    ...     cash_and_equivalents="25000000",
    ...     quarter="Q1",
    ...     year="2024"
    ... )
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from .edgar_online_search_criteria import SecFiling

class FinancialStatementItems(BaseModel):
    """Financial statement items extracted from SEC filings.
    
    Represents standardized financial metrics from 10-K and 10-Q filings,
    focusing on key performance indicators and balance sheet items.
    
    Attributes:
        revenue (str): Total revenue for the period, as reported in income statement
        operating_income (str): Operating income/loss before interest and taxes
        net_income (str): Net income/loss attributable to common shareholders
        eps_basic (str): Basic earnings per share, calculated per SEC guidelines
        eps_diluted (str): Diluted earnings per share, including potential dilution
        cash_and_equivalents (str): Cash and cash equivalents from balance sheet
        quarter (str): Fiscal quarter identifier (Q1-Q4)
        year (str): Fiscal year of the report
        
    Note:
        All monetary values are stored as strings to preserve exact values
        as reported in SEC filings, avoiding floating-point precision issues.
    """
    revenue: str = Field(..., description="Total revenue for the period")
    operating_income: str = Field(..., description="Operating income/loss")
    net_income: str = Field(..., description="Net income/loss")
    eps_basic: str = Field(..., description="Basic earnings per share")
    eps_diluted: str = Field(..., description="Diluted earnings per share")
    cash_and_equivalents: str = Field(..., description="Cash and cash equivalents")
    quarter: str = Field(..., pattern="^Q[1-4]$", description="Fiscal quarter (Q1-Q4)")
    year: str = Field(..., min_length=4, max_length=4, description="Fiscal year")

    @field_validator('quarter')
    @classmethod
    def validate_quarter(cls, v):
        if not v in {'Q1', 'Q2', 'Q3', 'Q4'}:
            raise ValueError('Quarter must be Q1, Q2, Q3, or Q4')
        return v
