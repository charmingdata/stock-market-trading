"""Models for SEC EDGAR filing data and financial metrics.

This module provides Pydantic models for representing SEC EDGAR filings
and their associated financial metrics. It includes validation for:
- CIK (Central Index Key) numbers
- SEC form types (10-K, 10-Q, etc.)
- Document URLs
- Financial metrics

The models support both basic filing metadata and detailed financial metrics
extracted from the filing documents.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class SecFiling(BaseModel):
    """Base model for SEC EDGAR filing metadata.
    
    Attributes:
        cik: SEC Central Index Key (10 digits, zero-padded)
        form_type: SEC form type (10-K, 10-Q, 8-K, etc.)
        filing_date: Date the filing was submitted
        document_url: URL to the filing on sec.gov
        accession_number: SEC accession number for the filing
        file_number: SEC file number
        description: Optional description of the filing
    
    Example:
        >>> filing = SecFiling(
        ...     cik="1318605",
        ...     form_type="10-Q",
        ...     filing_date="2025-05-15",
        ...     document_url="https://www.sec.gov/...",
        ...     accession_number="0001564590-25-012345",
        ...     file_number="001-34756"
        ... )
    """
    cik: str
    form_type: str
    filing_date: datetime
    document_url: str
    accession_number: str
    file_number: str
    description: str = ""

    @field_validator('cik')
    @classmethod
    def validate_cik(cls, v):
        if not v.isdigit() or len(v) > 10:
            raise ValueError('CIK must be a numeric string of up to 10 digits')
        return v.zfill(10)  # Pad with leading zeros to 10 digits

    @field_validator('form_type')
    @classmethod
    def validate_form_type(cls, v):
        valid_types = {'10-K', '10-Q', '8-K', '20-F', '6-K'}
        if v not in valid_types:
            raise ValueError(f'Form type must be one of: {valid_types}')
        return v

    @field_validator('document_url')
    @classmethod
    def validate_url(cls, v):
        if not v.startswith('https://www.sec.gov/'):
            raise ValueError('Document URL must be from sec.gov domain')
        return v
    
class FinancialMetrics(BaseModel):
    """Financial metrics extracted from SEC filings."""
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

# ...existing SecFiling class code...

class FilingWithMetrics(SecFiling):
    """SEC filing with extracted financial metrics."""
    company_name: str = Field(..., min_length=1)
    metrics: Optional[FinancialMetrics] = Field(None, description="Extracted financial metrics")