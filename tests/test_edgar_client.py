import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import sys
import os
from typing import Dict
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.edgar_client import EdgarClient, EdgarMetrics

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
    
    # Test the client
    with patch('aiohttp.ClientSession', return_value=mock_session):
        async with EdgarClient() as client:
            session_id = await client._create_session()
            
            # Verify results
            assert session_id == "test-session-123"
            assert client.session is not None
            assert isinstance(session_id, str)
            
            # Verify mock calls
            mock_session.post.assert_called_once()
            mock_response.json.assert_called_once()
                    
@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_session():
    """Integration test using real MCP server."""
    async with EdgarClient() as client:
        session_id = await client._create_session()
        assert session_id is not None
        assert len(session_id) > 0

@pytest.mark.asyncio
async def test_tesla_10q_metrics():
    """Test Tesla metrics retrieval and validation."""
    mock_response = {
            "cik": "1318605",
            "company_name": "Tesla, Inc.",
            "form_type": "10-Q",
            "filing_date": datetime.now().isoformat(),
            "quarter": "Q1",
            "revenue": 23.33,
            "net_income": 2.51,
            "eps_basic": 0.85,
            "document_url": "https://www.sec.gov/Archives/123"
        }
    
    async with EdgarClient() as client:
        metrics = await client.get_latest_10q_metrics(
                cik="1318605", 
                mock_data=mock_response
            )
        
        # Type checking
        assert isinstance(metrics, EdgarMetrics)
        assert isinstance(metrics.filing_date, datetime)
        
        # Content validation
        assert metrics.cik == "1318605"
        assert metrics.company_name == "Tesla, Inc."
        assert metrics.form_type == "10-Q"
        assert metrics.quarter in ["Q1", "Q2", "Q3", "Q4"]
        assert isinstance(metrics.revenue, float)
        assert isinstance(metrics.net_income, float)
        assert isinstance(metrics.eps_basic, float)

@pytest.mark.asyncio
async def test_error_handling():
    """Test error cases and handling."""
    async with EdgarClient() as client:
        with pytest.raises(ValueError):
            await client.get_latest_10q_metrics(cik="invalid")
