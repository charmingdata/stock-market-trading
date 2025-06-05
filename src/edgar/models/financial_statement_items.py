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
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class FinancialStatementItems(BaseModel):
    """Financial statement items extracted from SEC filings.
    
    Represents standardized financial metrics from 10-K and 10-Q filings,
    focusing on key performance indicators and balance sheet items.
    
    Attributes:
        cik: SEC Central Index Key (10 digits)
        company_name: Full legal company name
        form_type: SEC form type (10-K or 10-Q)
        filing_date: Date the filing was submitted
        document_url: URL to the filing document on sec.gov
        fiscal_year: Fiscal year of the report
        fiscal_quarter: Fiscal quarter identifier (Q1-Q4), None for annual reports
        
        revenue: Total revenue for the period, as reported in income statement
        operating_income: Operating income/loss before interest and taxes
        net_income: Net income/loss attributable to common shareholders
        eps_basic: Basic earnings per share, calculated per SEC guidelines
        eps_diluted: Diluted earnings per share, including potential dilution
        cash_and_equivalents: Cash and cash equivalents from balance sheet
        
    Note:
        All monetary values are stored as strings to preserve exact values
        as reported in SEC filings, avoiding floating-point precision issues.
    """
    # Filing reference information
    cik: str = Field(..., pattern=r'^\d{10}$')
    company_name: str = Field(..., min_length=1)
    form_type: str = Field(..., pattern=r'^10-[KQ]$')
    filing_date: datetime
    document_url: str = Field(..., pattern=r'^https://www\.sec\.gov/.*$')
    
    # Fiscal period information
    fiscal_year: int = Field(..., ge=1900, le=2100)
    fiscal_quarter: Optional[str] = Field(
        None, 
        description="Fiscal quarter (Q1-Q4), applicable for 10-Q filings"
    )
    
    # Financial metrics - all stored as strings to preserve exact reported values
    revenue: str = Field(..., description="Total revenue for the period")
    operating_income: str = Field(..., description="Operating income/loss")
    net_income: str = Field(..., description="Net income/loss")
    eps_basic: str = Field(..., description="Basic earnings per share")
    eps_diluted: str = Field(..., description="Diluted earnings per share")
    cash_and_equivalents: str = Field(..., description="Cash and cash equivalents")
    
    @field_validator('fiscal_quarter')
    @classmethod
    def validate_fiscal_quarter(cls, v, info):
        """Ensure fiscal_quarter is present for 10-Q and absent for 10-K."""
        form_type = info.data.get('form_type')
        if form_type == '10-Q' and not v:
            raise ValueError("fiscal_quarter is required for 10-Q filings")
        if form_type == '10-K' and v:
            raise ValueError("fiscal_quarter should not be set for 10-K filings")
        if v and v not in {'Q1', 'Q2', 'Q3', 'Q4'}:
            raise ValueError('Quarter must be Q1, Q2, Q3, or Q4')
        return v
    
    @classmethod
    def from_sec_filing(cls, filing, financial_data: dict) -> 'FinancialStatementItems':
        """Create FinancialStatementItems from a SecFiling and extracted data.
        
        Args:
            filing: SecFiling object containing metadata
            financial_data: Dictionary of extracted financial metrics
            
        Returns:
            FinancialStatementItems: The populated financial data object
            
        Raises:
            ValueError: If required financial data fields are missing
        """
        return cls(
            cik=filing.cik,
            company_name=filing.company_name,
            form_type=filing.form_type,
            filing_date=filing.submission_date,
            document_url=filing.document_url,
            fiscal_year=filing.fiscal_year,
            fiscal_quarter=filing.fiscal_quarter,
            revenue=financial_data['revenue'],
            operating_income=financial_data['operating_income'],
            net_income=financial_data['net_income'],
            eps_basic=financial_data['eps_basic'],
            eps_diluted=financial_data['eps_diluted'],
            cash_and_equivalents=financial_data['cash_and_equivalents']
        )
    
    @property
    def fiscal_period_display(self) -> str:
        """Human-readable fiscal period (e.g., 'FY 2024' or 'Q2 2024')."""
        if self.form_type == '10-K':
            return f"FY {self.fiscal_year}"
        return f"{self.fiscal_quarter} {self.fiscal_year}"
    
    @property
    def is_annual(self) -> bool:
        """Whether this represents an annual report (10-K)."""
        return self.form_type == '10-K'
    
    @property
    def is_quarterly(self) -> bool:
        """Whether this represents a quarterly report (10-Q)."""
        return self.form_type == '10-Q'