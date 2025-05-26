"""Models for SEC EDGAR filing data and financial metrics.

This module, and its sibling metrics.py, provide Pydantic models for representing SEC EDGAR filings
and their associated financial metrics. It includes validation for:
- CIK (Central Index Key) numbers
- SEC form types (10-K, 10-Q, etc.)
- Document URLs
- Financial metrics

The models support both basic filing metadata and detailed financial metrics
extracted from the filing documents.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator

class SecFiling(BaseModel):
    """SEC EDGAR filing metadata.
    
    Attributes:
        cik: SEC Central Index Key (10 digits)
        company_name: Full legal company name
        form_type: SEC form type (10-K or 10-Q)
        filing_date: Date the filing was submitted
        file_number: SEC assigned file number
        document_url: URL to the filing document on sec.gov
    """
    cik: str = Field(..., pattern=r'^\d{10}$')
    company_name: str = Field(..., min_length=1)
    form_type: str = Field(..., pattern=r'^10-[KQ]$')
    filing_date: datetime
    file_number: str
    document_url: str = Field(..., pattern=r'^https://www\.sec\.gov/.*$')

class EdgarSearchCriteria(BaseModel):
    """SEC EDGAR filing search criteria.
    
    Supports two search modes:
    1. Date-based: Search by filing date range
    2. Fiscal period: Search by fiscal year and optional quarter

    Attributes:
        cik: SEC Central Index Key (10 digits, zero-padded)
        form_type: SEC form type (10-K or 10-Q)
        filing_date_start: Start date for filing search (date-based mode)
        filing_date_end: Optional end date (date-based mode)
        fiscal_year: Year for fiscal period search (1900-2100)
        fiscal_quarter: Optional quarter for 10-Q filings (Q1-Q4)

    Examples:
        Date-based search:
        >>> search = EdgarSearchCriteria(
        ...     cik="0001318605",
        ...     form_type="10-K",
        ...     filing_date_start=datetime(2024, 1, 1),
        ...     filing_date_end=datetime(2024, 12, 31)
        ... )

        Fiscal period search:
        >>> search = EdgarSearchCriteria.for_fiscal_period(
        ...     cik="0001318605",
        ...     year=2024,
        ...     quarter="Q1"
        ... )
    """
    cik: str = Field(..., pattern=r'^\d{10}$')
    form_type: str = Field(..., pattern=r'^10-[KQ]$')
    
    # Date-based search (mutually exclusive with fiscal period)
    filing_date_start: Optional[datetime] = None
    filing_date_end: Optional[datetime] = None
    
    # Fiscal period search
    fiscal_year: Optional[int] = Field(None, ge=1900, le=2100)
    fiscal_quarter: Optional[Literal['Q1', 'Q2', 'Q3', 'Q4']] = None

    @model_validator(mode='before')
    @classmethod
    def validate_search_criteria(cls, values):
        """Ensure either date range or fiscal period is provided, not both."""
        date_search = bool(values.get('filing_date_start'))
        fiscal_search = bool(values.get('fiscal_year'))
        
        if date_search and fiscal_search:
            raise ValueError("Cannot specify both date range and fiscal period")
        if not (date_search or fiscal_search):
            raise ValueError("Must specify either date range or fiscal period")
            
        return values

    @classmethod
    def for_fiscal_period(cls, 
                         cik: str,
                         year: int,
                         quarter: Optional[str] = None) -> "EdgarSearchCriteria":
        """Create search criteria for a specific fiscal period.
        
        Args:
            cik: Company CIK number
            year: Fiscal year (e.g., 2024)
            quarter: Optional quarter (Q1-Q4)
        """
        form_type = "10-Q" if quarter else "10-K"
        return cls(
            cik=cik,
            form_type=form_type,
            fiscal_year=year,
            fiscal_quarter=quarter
        )
    
    @classmethod
    async def to_sec_filing(cls, search_result: dict) -> SecFiling:
        """Convert SEC EDGAR search result to SecFiling model.
        
        Args:
            search_result: Raw search result from SEC EDGAR API
            
        Returns:
            SecFiling: Validated filing metadata
        """
        return SecFiling(
            cik=search_result['cik'],
            company_name=search_result['company_name'],
            form_type=search_result['form_type'],
            filing_date=datetime.fromisoformat(search_result['filing_date']),
            file_number=search_result['file_number'],
            document_url=search_result['document_url']
        )

    def matches_filing(self, filing: SecFiling) -> bool:
        """Check if a SecFiling matches this search criteria.
        
        Args:
            filing: SecFiling instance to check
            
        Returns:
            bool: True if filing matches criteria
        """
        if filing.cik != self.cik or filing.form_type != self.form_type:
            return False
            
        if self.fiscal_year:
            # TODO: Implement fiscal period matching
            return True
            
        if self.filing_date_start:
            return (self.filing_date_start <= filing.filing_date and 
                   (not self.filing_date_end or filing.filing_date <= self.filing_date_end))
                   
        return True