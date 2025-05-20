"""SEC EDGAR client for fetching financial metrics via MCP browser automation."""

import aiohttp
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Optional

class EdgarMetrics(BaseModel):
    """Financial metrics from EDGAR filing."""
    cik: str
    company_name: str
    form_type: str = Field(..., pattern=r'^10-[KQ]$')
    filing_date: datetime
    quarter: Optional[str] = Field(None, pattern=r'^Q[1-4]$')
    revenue: float = Field(..., ge=0)
    net_income: float
    eps_basic: float
    document_url: str = Field(..., pattern=r'^https://[^\s/$.?#].[^\s]*$')

class EdgarClient:
    """Client for fetching and parsing SEC EDGAR filings."""
    
    def __init__(
        self, 
        mcp_server_url: str = "http://localhost:3000",
        user_agent: str = "Test Company test@example.com"
    ):
        """Initialize the client.
        
        Args:
            mcp_server_url: URL of the MCP browser automation server
            user_agent: User agent string for SEC EDGAR access
        """
        self.mcp_server_url = mcp_server_url
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "application/json",
        }
        self.session: Optional[aiohttp.ClientSession] = None
        self.session_id: Optional[str] = None

    async def __aenter__(self):
        """Enable async context management."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup session on exit."""
        if self.session:
            await self.session.close()
        self.session = None
        self.session_id = None

    async def _create_session(self) -> str:
        """Create a new browser automation session."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async with.")
            
        try:
            # Use ClientResponse context manager
            response = await self.session.post(
                f"{self.mcp_server_url}/session",
                headers=self.headers
            )
            
            if response.status != 200:
                raise ConnectionError(f"Session creation failed: {response.status}")
                
            data = await response.json()
            return data["sessionId"]
            
        except Exception as e:
            raise ConnectionError(f"Failed to create session: {str(e)}")

    async def get_latest_10q_metrics(
        self, 
        cik: str, 
        mock_data: Optional[Dict] = None
    ) -> EdgarMetrics:
        """Get latest 10-Q financial metrics for a company.
        
        Args:
            cik: Company CIK number
            mock_data: Optional mock response for testing
        
        Returns:
            EdgarMetrics: Validated filing metrics
            
        Raises:
            ValueError: If CIK is invalid
            ConnectionError: If MCP server request fails
        """
        if not cik.isdigit():
            raise ValueError("CIK must be numeric")

        if mock_data:
            return EdgarMetrics.model_validate(mock_data)
            
        if not self.session_id:
            self.session_id = await self._create_session()

        async with self.session.post(
            f"{self.mcp_server_url}/session/{self.session_id}/execute",
            headers=self.headers,
            json={"cik": cik, "form_type": "10-Q"}
        ) as response:
            if response.status != 200:
                raise ConnectionError(f"Failed to fetch metrics: {response.status}")
            data = await response.json()
            return EdgarMetrics.model_validate(data)
