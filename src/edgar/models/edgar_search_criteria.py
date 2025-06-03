"""Models for SEC EDGAR search criteria and results.

This module provides Pydantic models for representing SEC EDGAR search criteria
and operations. It includes functionality for:
- Creating search criteria by date range or fiscal period
- Converting search results to filing objects
- Matching filings against search criteria
"""

from datetime import datetime
from typing import Optional, Literal, Dict, Any, TYPE_CHECKING, ForwardRef
from pydantic import BaseModel, Field, model_validator

from .edgar_filings import SecFiling
from .financial_statement_items import FinancialStatementItems

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from .financial_statement_items import FinancialStatementItems

# Create a forward reference for type hints
FinancialItemsRef = ForwardRef('FinancialStatementItems')

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
        
        A convenience method for creating search criteria based on fiscal period.
        The form_type is automatically set based on whether quarter is specified.
        
        Args:
            cik: Company CIK number (10 digits)
            year: Fiscal year (e.g., 2024)
            quarter: Optional quarter (Q1-Q4) for quarterly reports
            
        Returns:
            EdgarSearchCriteria configured for fiscal period search
        """
        form_type = "10-Q" if quarter else "10-K"
        return cls(
            cik=cik,
            form_type=form_type,
            fiscal_year=year,
            fiscal_quarter=quarter
        )
    
    async def get_financial_data(self) -> Optional[FinancialStatementItems]:
        """Extract financial data based on the search criteria.
        
        Searches for a filing matching the criteria and extracts its financial data.
        In a production implementation, this would first find the actual filing.
        
        Returns:
            Extracted financial statement items, or None if not found
            
        Raises:
            ConnectionError: If connection to SEC EDGAR fails
            ValueError: If financial data cannot be extracted
        """
        # This would integrate with your scraper functionality
        from ..client.scraper import EdgarScraper
        from ..models import FinancialStatementItems
        
        # First need to find the actual filing
        # In a real implementation, this would search for the filing
        # For now, just create a mock filing based on search criteria
        filing = SecFiling(
            cik=self.cik,
            company_name="Example Corp",  # This would come from search
            form_type=self.form_type,
            fiscal_year=self.fiscal_year or datetime.now().year,
            fiscal_quarter=self.fiscal_quarter,
            submission_date=datetime.now(),  # Placeholder
            file_number="001-12345",  # Placeholder
            document_url="https://www.sec.gov/mock"  # Placeholder
        )
        
        # Now extract data from the filing
        scraper = EdgarScraper()
        if self.form_type == '10-K':
            return await scraper.extract_annual_income_statement(
                filing, fiscal_year=self.fiscal_year
            )
        else:
            return await scraper.extract_quarterly_income_statement(
                filing, quarter=self.fiscal_quarter, fiscal_year=self.fiscal_year
            )
        
    @classmethod
    async def to_sec_filing(cls, search_result: dict) -> SecFiling:
        """Convert SEC EDGAR search result to SecFiling model.
        
        This method transforms raw search results from the SEC EDGAR API into a structured
        SecFiling object. It handles date parsing, fiscal period detection, and ensures
        all required fields are properly formatted.
        
        Args:
            search_result: Raw search result dictionary from SEC EDGAR API containing
                          keys like 'cik', 'company_name', 'form_type', 'filing_date',
                          'file_number', and 'document_url'. May optionally include
                          'fiscal_year' and 'quarter'.
                
        Returns:
            SecFiling: A validated filing metadata object
            
        Raises:
            ValueError: If required fields are missing from the search result
        """
        # Convert date string to datetime
        submission_date = datetime.fromisoformat(search_result['filing_date'])
        
        # Extract fiscal period information
        fiscal_year = search_result.get('fiscal_year') or submission_date.year
        fiscal_quarter = None
        if search_result.get('form_type') == '10-Q':
            # Try to determine quarter from submission date or form title
            if 'quarter' in search_result:
                fiscal_quarter = f"Q{search_result['quarter']}"
            else:
                month = submission_date.month
                fiscal_quarter = f"Q{(month-1)//3 + 1}"  # Simple mapping
        
        return SecFiling(
            cik=search_result['cik'],
            company_name=search_result['company_name'],
            form_type=search_result['form_type'],
            fiscal_year=fiscal_year,
            fiscal_quarter=fiscal_quarter,
            submission_date=submission_date,
            file_number=search_result['file_number'],
            document_url=search_result['document_url']
        )

    def matches_filing(self, filing: SecFiling) -> bool:
        """Check if a SecFiling matches this search criteria.
        
        Determines whether a filing matches the current search criteria based on
        CIK, form type, fiscal period, and/or filing date range.
        
        Args:
            filing: SecFiling instance to check
            
        Returns:
            True if filing matches all specified criteria, False otherwise
        """
        if filing.cik != self.cik or filing.form_type != self.form_type:
            return False
            
        if self.fiscal_year:
            if filing.fiscal_year != self.fiscal_year:
                return False
            if self.fiscal_quarter and filing.fiscal_quarter != self.fiscal_quarter:
                return False
            return True
            
        if self.filing_date_start:
            return (self.filing_date_start <= filing.submission_date and
                  (not self.filing_date_end or filing.submission_date <= self.filing_date_end))
                  
        return True

# Update forward references
EdgarSearchCriteria.model_rebuild()