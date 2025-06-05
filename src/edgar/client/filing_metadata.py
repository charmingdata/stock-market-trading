async def get_filing_metadata(
    self,
    cik: str,
    form_type: str,
    year: int
) -> Dict[str, Any]:
    """Get metadata for a specific filing.
    
    Args:
        cik: Company CIK number
        form_type: Form type (10-K or 10-Q)
        year: Fiscal year
        
    Returns:
        Dictionary with filing metadata
        
    Raises: 
        ValueError: If CIK is invalid
        ConnectionError: If MCP server request fails
    """
    filing = await self.get_filing(cik, form_type, year)
    return filing.metadata if filing else {}

async def get_filing_summary(
    self,
    cik: str,
    form_type: str,
    year: int
) -> Dict[str, Any]:
    """Get a summary of a specific filing.
    
    Args:
        cik: Company CIK number
        form_type: Form type (10-K or 10-Q)
        year: Fiscal year
        
    Returns:
        Dictionary with filing summary
        
    Raises:
        ValueError: If CIK is invalid
        ConnectionError: If MCP server request fails
    """
    filing = await self.get_filing(cik, form_type, year)
    return filing.summary if filing else {}

async def get_filing_index(
    self,
    cik: str,
    form_type: str,
    year: int
) -> int:
    """Get the index of a specific filing in the company's filing history.
    
    Args:
        cik: Company CIK number
        form_type: Form type (10-K or 10-Q)
        year: Fiscal year
    Returns:
        int: Index of the filing in the company's filing history
    Raises:
        ValueError: If CIK is invalid
        ConnectionError: If MCP server request fails
    """
    filings = await self.get_filing_history(cik, form_type, year)
    for index, filing in enumerate(filings):
        if filing.cik == cik and filing.form_type == form_type and filing.year == year:
            return index
    raise ValueError(f"Filing not found for CIK {cik}, form type {form_type}, year {year}")
