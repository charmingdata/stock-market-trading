from ..models import SecFiling
from typing import Optional, List

async def get_company_filings(
        cik: str,
        form_types: Optional[list[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> list[SecFiling]:
        """Get all filings for a company.
        
        Args:
            cik: Company CIK number
            form_types: List of form types to filter by (e.g. ["10-K", "10-Q"])
            start_date: Start date for filtering filings
            end_date: End date for filtering filings
            
        Returns:
            List of SecFiling objects
            
        Raises:
            ValueError: If CIK is invalid
            ConnectionError: If MCP server request fails
        """
        if not cik.isdigit() or len(cik) != 10:
            raise ValueError("CIK must be a 10-digit numeric string")
        
        # This is a placeholder for the actual logic to fetch filings
        # In practice, this would involve searching EDGAR and returning matching filings
        return [SecFiling()]
    
async def _get_filing_url(edgar_url: str, cik: str, form_type: str, year: int) -> str:
        """Get the URL for a specific filing.
        
        Args:
            cik: Company CIK number
            form_type: Form type (10-K or 10-Q)
            year: Fiscal year
            
        Returns:
            str: URL of the filing
            
        Raises:
            ValueError: If CIK is invalid
        """
        if not cik.isdigit() or len(cik) != 10:
            raise ValueError("CIK must be a 10-digit numeric string")
        
        # This is a placeholder for the actual logic to construct the filing URL
        # In practice, this would involve searching EDGAR and finding the correct filing
        return f"{self.edgar_url}/filing/{cik}/{form_type}/{year}"
