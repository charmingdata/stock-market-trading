import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
import os
import sys
sys.path.append(
    (os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))))

from src.edgar.client.search_params import EdgarSearch
from src.edgar.models.edgar_filings import SecFiling

@pytest.mark.asyncio
async def test_search_tesla_filings():
    """Test SEC EDGAR search for Tesla filings."""
    search = EdgarSearch()
    
    # Create a sample filing to return from the mock
    sample_filing = SecFiling(
        cik="0001318605",
        company_name="Tesla, Inc.",
        form_type="10-K",
        filing_date=datetime.now(),
        document_url="https://www.sec.gov/Archives/123",
        file_number="001-12345",
        fiscal_year=2024,
        submission_date=datetime.now()
    )
    
    # Mock the find_company_filings method
    with patch.object(search, 'find_company_filings', return_value=[sample_filing]):
        results = await search.find_company_filings(
            company="TESLA",
            form_types=["10-K"],
            start_date="2024-01-01"
        )
        
        # Verify we got a result with expected structure
        assert len(results) == 1
        assert isinstance(results[0], SecFiling)
        assert results[0].company_name == "Tesla, Inc."
        assert results[0].form_type == "10-K"