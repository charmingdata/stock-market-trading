from ..mmodels import SecFiling
from typing import Dict, Any
from .scraper import EdgarScraper
from .session import MCPServerConnectionError

async def get_filing_by_index(
    self,
    cik: str,
    form_type: str,
    year: int,
    index: int
) -> SecFiling:
    """Get a specific filing by index in the company's filing history.
    
    Args:
        cik: Company CIK number
        form_type: Form type (10-K or 10-Q)
        year: Fiscal year
        index: Index of the filing in the history
    Returns:
        SecFiling: Filing object at the specified index
    Raises:
        ValueError: If CIK is invalid or index is out of range
        ConnectionError: If MCP server request fails
    """
    filings = await self.get_filing_history(cik, form_type, year)
    if index < 0 or index >= len(filings):
        raise ValueError(f"Index {index} out of range for CIK {cik}, form type {form_type}, year {year}")
    return filings[index]

async def get_filing_documents_by_index(
    self,
    cik: str,
    form_type: str,
    year: int,
    index: int
) -> list[str]:
    """Get document URLs for a filing by index.
    
    Args:
        cik: Company CIK number
        form_type: Form type (10-K or 10-Q)
        year: Fiscal year
        index: Index of the filing in the history
        
    Returns:
        List of document URLs for the specified filing
        
    Raises:
        ValueError: If CIK is invalid or index is out of range
        ConnectionError: If MCP server request fails
    """
    filing = await self.get_filing_by_index(cik, form_type, year, index)
    return filing.document_urls if filing else []

async def get_filing_text_by_index(
    self,
    cik: str,
    form_type: str,
    year: int,
    index: int
) -> str:
    """Get text content of a filing by index.
    
    Args:
        cik: Company CIK number
        form_type: Form type (10-K or 10-Q)
        year: Fiscal year
        index: Index of the filing in the history
        
    Returns:
        str: Text content of the specified filing
        
    Raises:
        ValueError: If CIK is invalid or index is out of range
        ConnectionError: If MCP server request fails
    """
    filing = await self.get_filing_by_index(cik, form_type, year, index)
    return filing.text_content if filing else ""

async def get_filing_html_by_index(
    self,
    cik: str,
    form_type: str,
    year: int,
    index: int
) -> str:
    """Get HTML content of a filing by index.
    
    Args:
        cik: Company CIK number
        form_type: Form type (10-K or 10-Q)
        year: Fiscal year
        index: Index of the filing in the history
        
    Returns:
        str: HTML content of the specified filing
        
    Raises:
        ValueError: If CIK is invalid or index is out of range
        ConnectionError: If MCP server request fails
    """
    filing = await self.get_filing_by_index(cik, form_type, year, index)
    return filing.html_content if filing else ""

async def get_filing_metadata_by_index(
    self,
    cik: str,
    form_type: str,
    year: int,
    index: int
) -> Dict[str, Any]:
    """Get metadata for a filing by index.
    
    Args:
        cik: Company CIK number
        form_type: Form type (10-K or 10-Q)
        year: Fiscal year
        index: Index of the filing in the history
        
    Returns:
        Dictionary with filing metadata
        
    Raises:
        ValueError: If CIK is invalid or index is out of range
        ConnectionError: If MCP server request fails
    """
    filing = await self.get_filing_by_index(cik, form_type, year, index)
    return filing.metadata if filing else {}

async def get_filing_summary_by_index(
    self,
    cik: str,
    form_type: str,
    year: int,
    index: int
) -> Dict[str, Any]:
    """Get summary of a filing by index.
    
    Args:
        cik: Company CIK number
        form_type: Form type (10-K or 10-Q)
        year: Fiscal year
        index: Index of the filing in the history
        
    Returns:
        Dictionary with filing summary
        
    Raises:
        ValueError: If CIK is invalid or index is out of range
        ConnectionError: If MCP server request fails
    """
    filing = await self.get_filing_by_index(cik, form_type, year, index)
    return filing.summary if filing else {}

async def get_filing_history_by_index(
    self,
    cik: str,
    form_type: str,
    year: int,
    index: int
) -> list[SecFiling]:
    """Get filing history for a specific company by index.
    
    Args:
        cik: Company CIK number
        form_type: Form type (10-K or 10-Q)
        year: Fiscal year
        index: Index of the filing in the history
        
    Returns:
        List of SecFiling objects representing filing history
        
    Raises:
        ValueError: If CIK is invalid or index is out of range
        ConnectionError: If MCP server request fails
    """
    filings = await self.get_filing_history(cik, form_type, year)
    if index < 0 or index >= len(filings):
        raise ValueError(f"Index {index} out of range for CIK {cik}, form type {form_type}, year {year}")
    return filings[:index + 1]

async def get_filing_index_by_index(
    self,
    cik: str,
    form_type: str,
    year: int,
    index: int
) -> int:
    """Get the index of a specific filing in the company's filing history by index.
    
    Args:
        cik: Company CIK number
        form_type: Form type (10-K or 10-Q)
        year: Fiscal year
        index: Index of the filing in the history
    Returns:
        int: Index of the filing in the company's filing history
    Raises:
        ValueError: If CIK is invalid or index is out of range
        ConnectionError: If MCP server request fails
    """
    filings = await self.get_filing_history(cik, form_type, year)
    if index < 0 or index >= len(filings):
        raise ValueError(f"Index {index} out of range for CIK {cik}, form type {form_type}, year {year}")
    for i, filing in enumerate(filings):
        if filing.cik == cik and filing.form_type == form_type and filing.year == year:
            return i
    raise ValueError(f"Filing not found for CIK {cik}, form type {form_type}, year {year}")

async def get_filing_by_cik(
    self,
    cik: str,
    form_type: str,
    year: int
) -> SecFiling:
    """Get a specific filing by CIK, form type, and year.
    
    Args:
        cik: Company CIK number
        form_type: Form type (10-K or 10-Q)
        year: Fiscal year
        
    Returns:
        SecFiling: Parsed filing data
        
    Raises:
        ValueError: If CIK is invalid
        ConnectionError: If MCP server request fails
    """
    filing_url = await self._get_filing_url(cik, form_type, year)
    if not await self.navigate(filing_url):
        raise MCPServerConnectionError(self.mcp_server_url, "Failed to navigate to filing URL")
    
    content = await self.get_page_content()
    scraper = EdgarScraper(content)
    filing = scraper.parse_filing()
    
    if not filing:
        raise ValueError(f"No filing found for CIK {cik}, form type {form_type}, year {year}")
    
    return filing
