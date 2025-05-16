"""SEC EDGAR client for fetching financial metrics via MCP browser automation."""

from typing import Dict, Optional
import aiohttp

class EdgarClient:
    """Client for fetching and parsing SEC EDGAR filings."""
    
    def __init__(self, mcp_server_url: str = "http://localhost:3000"):
        """Initialize the client.
        
        Args:
            mcp_server_url: URL of the MCP browser automation server
        """
        self.mcp_server_url = mcp_server_url
        self.headers = {
            "User-Agent": "Your Company Name yourname@domain.com",
            "Accept": "application/json",
        }
        self.session_id = None

    async def _create_session(self) -> str:
        """Create a new browser automation session"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.mcp_server_url}/session",
                headers=self.headers
            ) as response:
                data = await response.json()
                return data["sessionId"]

    async def get_latest_10q_metrics(self, cik: str) -> Optional[Dict]:
        """Get latest 10-Q financial metrics for a company"""
        if not self.session_id:
            self.session_id = await self._create_session()

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.mcp_server_url}/session/{self.session_id}/execute",
                headers=self.headers,
                json={"cik": cik, "form_type": "10-Q"}
            ) as response:
                return await response.json()
            