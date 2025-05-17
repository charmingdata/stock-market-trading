import pytest
import asyncio
from src.edgar_client import EdgarClient

@pytest.mark.asyncio
async def test_tesla_10q_metrics():
    # Initialize client
    client = EdgarClient()
    
    # Get Tesla's Q1 2025 10-Q metrics
    metrics = await client.get_latest_10q_metrics(cik="1318605")
    
    # Assert response structure and content
    assert metrics is not None
    assert metrics["cik"] == "1318605"
    assert metrics["form_type"] == "10-Q"
    assert metrics["company_name"] == "Tesla, Inc."
    
    # Assert financial metrics
    assert "revenue" in metrics["metrics"]
    assert "net_income" in metrics["metrics"]
    assert "eps_basic" in metrics["metrics"]
    assert metrics["metrics"]["quarter"] == "Q1"
    assert metrics["metrics"]["year"] == "2025"

    # Assert document URL format
    assert "sec.gov/Archives/edgar/data" in metrics["document_url"]