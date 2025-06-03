"""Models for SEC EDGAR filing metadata.

This module provides Pydantic models for representing SEC EDGAR filings.
It includes validation for:
- CIK (Central Index Key) numbers
- SEC form types (10-K, 10-Q, etc.)
- Document URLs
- Filing metadata and fiscal periods

The models support both basic filing metadata and relationships between filings.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator, field_validator

class SecFiling(BaseModel):
    """SEC EDGAR filing metadata.
    
    Attributes:
        cik: SEC Central Index Key (10 digits)
        company_name: Full legal company name
        display_name: Standardized company name for display purposes
        form_type: SEC form type (10-K or 10-Q)
        fiscal_year: Fiscal year of the filing
        fiscal_quarter: Fiscal quarter (Q1-Q4), applicable for 10-Q filings
        submission_date: Date when the filing was submitted to SEC
        file_number: SEC assigned file number
        document_url: URL to the filing document on sec.gov
    """
    cik: str = Field(..., pattern=r'^\d{10}$')
    company_name: str = Field(..., min_length=1)
    display_name: Optional[str] = None
    form_type: str = Field(..., pattern=r'^10-[KQ]$')
    
    # Filing identification
    fiscal_year: int = Field(..., ge=1900, le=2100)
    fiscal_quarter: Optional[str] = Field(
        None, 
        description="Fiscal quarter (Q1-Q4), applicable for 10-Q filings"
    )
    
    # Keep filing_date for reference/sorting but make its purpose clear
    submission_date: datetime = Field(
        ..., 
        description="Date when the filing was submitted to SEC"
    )
    
    # Other metadata
    file_number: str
    document_url: str = Field(..., pattern=r'^https://www\.sec\.gov/.*$')
    
    @property
    def fiscal_period_display(self) -> str:
        """Human-readable fiscal period (e.g., 'FY 2024' or 'Q2 2024')."""
        if self.form_type == '10-K':
            return f"FY {self.fiscal_year}"
        return f"{self.fiscal_quarter} {self.fiscal_year}"
    
    @property
    def is_annual(self) -> bool:
        """Whether this is an annual report (10-K)."""
        return self.form_type == '10-K'
    
    @property
    def is_quarterly(self) -> bool:
        """Whether this is a quarterly report (10-Q)."""
        return self.form_type == '10-Q'
    
    @property
    def filing_age_days(self) -> int:
        """Age of filing in days from submission date."""
        return (datetime.now() - self.submission_date).days
    
    def __lt__(self, other: 'SecFiling') -> bool:
        """Compare filings chronologically."""
        if self.fiscal_year != other.fiscal_year:
            return self.fiscal_year < other.fiscal_year
        
        # For same year, quarterly reports are ordered by quarter
        if self.is_quarterly and other.is_quarterly:
            # Extract quarter number for comparison
            self_q = int(self.fiscal_quarter[1])
            other_q = int(other.fiscal_quarter[1])
            return self_q < other_q
        
        # Annual reports come after all quarterly reports of the same year
        if self.is_quarterly and other.is_annual:
            return True
        if self.is_annual and other.is_quarterly:
            return False
        
        # Default to submission date if all else is equal
        return self.submission_date < other.submission_date

    @model_validator(mode='after')
    def canonicalize_company_name(self):
        """Set standardized display name if available."""
        from ..search.company_mapping import get_standardized_company_name
        
        # Set display_name based on mapping if available
        standard_name = get_standardized_company_name(self.cik)
        if standard_name:
            self.display_name = standard_name
        else:
            self.display_name = self.company_name
            
        return self
    
    @classmethod
    def from_search_result(cls, result: Dict[str, Any]) -> 'SecFiling':
        """Create a SecFiling from a search result dictionary.
        
        Args:
            result: Dictionary containing filing metadata from a search operation
            
        Returns:
            A new SecFiling instance populated from the search result
            
        Raises:
            ValueError: If required fields are missing from the result
        """
        # Convert date string to datetime
        submission_date = datetime.fromisoformat(result['filing_date'])
        
        # Extract fiscal period information
        fiscal_year = result.get('fiscal_year') or submission_date.year
        fiscal_quarter = None
        if result.get('form_type') == '10-Q':
            # Try to determine quarter from submission date or form title
            if 'quarter' in result:
                fiscal_quarter = f"Q{result['quarter']}"
            else:
                month = submission_date.month
                fiscal_quarter = f"Q{(month-1)//3 + 1}"  # Simple mapping
        
        return cls(
            cik=result['cik'],
            company_name=result['company_name'],
            form_type=result['form_type'],
            fiscal_year=fiscal_year,
            fiscal_quarter=fiscal_quarter,
            submission_date=submission_date,
            file_number=result['file_number'],
            document_url=result['document_url']
        )
    
    # Validate fiscal_quarter based on form_type
    @field_validator('fiscal_quarter')
    @classmethod
    def validate_fiscal_quarter(cls, v, info):
        """Ensure fiscal_quarter is present for 10-Q and absent for 10-K."""
        form_type = info.data.get('form_type')
        if form_type == '10-Q' and not v:
            raise ValueError("fiscal_quarter is required for 10-Q filings")
        if form_type == '10-K' and v:
            raise ValueError("fiscal_quarter should not be set for 10-K filings")
        return v