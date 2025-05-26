import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from src.edgar.search import EdgarSearch
from src.edgar.models import SecFiling

@pytest.mark.asyncio
async def test_search_tesla_filings():
    """Test SEC EDGAR search for Tesla filings."""
    search = EdgarSearch()
    
    with pytest.raises(NotImplementedError):
        await search.find_company_filings(
            company="TESLA",
            form_types=["10-K", "10-Q"],
            start_date=datetime(2024, 1, 1)
        )
        