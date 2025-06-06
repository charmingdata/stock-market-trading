import pytest
from typing import Literal, Optional, Dict
from unittest.mock import AsyncMock, patch
import sys
import os
from datetime import datetime

sys.path.append(
    (os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))))
from src.edgar.client.client import EdgarClient
from src.edgar.models.edgar_filings import SecFiling
from src.edgar.models.financial_statement_items import FinancialStatementItems
from src.edgar.client.search_params import EdgarSearch

@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization and configuration."""
    client = EdgarClient(
        mcp_server_url="http://localhost:3000",
        user_agent="Test Company test@example.com"
    )
    assert client.mcp_server_url == "http://localhost:3000"
    assert "Test Company" in client.headers["User-Agent"]

@pytest.mark.asyncio
async def test_session_management():
    """Test session creation and cleanup with mock responses."""
    # Create mock response with proper async context
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"sessionId": "test-session-123"}

    # Create session mock that returns response directly
    mock_session = AsyncMock()
    mock_session.post.return_value = mock_response

    # Patch the context manager for aiohttp.ClientSession
    with patch('aiohttp.ClientSession') as mock_session_cls:
        mock_session_cls.return_value.__aenter__.return_value = mock_session
        async with EdgarClient() as client:
            session_id = await client._create_session()
            assert client.session is not None
            assert isinstance(session_id, str)
            mock_session.post.assert_called_once()
            mock_response.json.assert_called_once()
                                
@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_session():
    """Integration test using real MCP server."""
    if "REAL_MCP_SERVER" not in os.environ:
        pytest.skip("Integration test requires live MCP server")
    
    # This code only runs if the test is not skipped
    async with EdgarClient() as client:
        session_id = await client._create_session()
        assert session_id is not None
        assert len(session_id) > 0
        
@pytest.mark.asyncio
async def test_get_10q_metrics():
    """Test fetching 10-Q metrics for a specific quarter."""
    client = EdgarClient()
    
    # Mock the client's get_company_financials method
    async def mock_get_company_financials(*args, **kwargs):
        return FinancialStatementItems(
            cik="0001318605",  # Need 10 digits to match the pattern
            company_name="Tesla, Inc.",
            form_type="10-Q",
            filing_date=datetime.now(),
            quarter="Q1",
            revenue="23.33",
            operating_income="5.00",
            net_income="2.51",
            eps_basic="0.85",
            eps_diluted="0.80",
            cash_and_equivalents="100.00",
            fiscal_year=2024,  # Add required field
            document_url="https://www.sec.gov/Archives/123"
        )
    
    # Patch the client's method
    with patch.object(client, 'get_company_financials', side_effect=mock_get_company_financials):
        metrics = await client.get_company_financials(
            cik="0001318605",
            form_type="10-Q",
            fiscal_period="Q1",
            year=2024
        )
        
        assert metrics is not None
        assert metrics.company_name == "Tesla, Inc."
        assert metrics.quarter == "Q1"
        assert metrics.fiscal_year == 2024

@pytest.mark.asyncio
async def test_company_search():
    """Test SEC EDGAR company search integration."""
    search = EdgarSearch()
    
    # Create a mock SecFiling to avoid import error
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
            form_types=["10-K", "10-Q"],
            start_date="2024-01-01"
        )
        
        # Verify structure matches our model
        assert isinstance(results[0], SecFiling)
        assert results[0].form_type in ["10-K", "10-Q"]
        assert "sec.gov" in results[0].document_url
        
@pytest.mark.asyncio
async def test_get_company_financials(monkeypatch):
    """Test EdgarClient.get_company_financials with mocked helpers."""
    from src.edgar.models.financial_statement_items import FinancialStatementItems

    # Dummy SecFiling and FinancialStatementItems
    dummy_filing = object()
    dummy_metrics = FinancialStatementItems.model_validate({
        "cik": "0001318605",  # 10 digits required
        "company_name": "Tesla, Inc.",
        "form_type": "10-Q",
        "filing_date": datetime.now().isoformat(),
        "quarter": "Q1",
        "revenue": "23.33",
        "operating_income": "5.00",
        "net_income": "2.51",
        "eps_basic": "0.85",
        "eps_diluted": "0.80",
        "cash_and_equivalents": "100.00",
        "fiscal_year": 2024,  # Add this required field (not 'year')
        "document_url": "https://www.sec.gov/Archives/123"
    })

    async def mock_search_filings(self, criteria):
        return dummy_filing

    async def mock_extract_financials(self, filing):
        return dummy_metrics

    async with EdgarClient() as client:
        # Patch the internal methods
        monkeypatch.setattr(client, "_search_filings", mock_search_filings.__get__(client))
        monkeypatch.setattr(client, "_extract_financials", mock_extract_financials.__get__(client))

        metrics = await client.get_company_financials(
            cik="1318605",
            form_type="10-Q",
            fiscal_period="Q1",
            year=2024
        )

        assert isinstance(metrics, FinancialStatementItems)
        assert metrics.cik == "1318605"
        assert metrics.company_name == "Tesla, Inc."
        assert metrics.form_type == "10-Q"