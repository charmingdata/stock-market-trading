"""SEC EDGAR API client for fetching financial metrics via MCP browser automation."""
import aiohttp
import os
import logging
from typing import Optional, Dict, Literal, Any

from .scraper import EdgarScraper   
from ..models import SecFiling, EdgarSearchCriteria, FinancialStatementItems
from ..constants import (
    SEC_EDGAR_SEARCH_URL,
    SUPPORTED_FORM_TYPES,
    FiscalPeriodType
)

# Configure logging
logger = logging.getLogger(__name__)

# Environment variable for MCP server URL
MCP_SERVER_URL_ENV = "MCP_SERVER_URL"
DEFAULT_MCP_SERVER_URL = "http://localhost:3000"
DEFAULT_USER_AGENT = "Test Company test@example.com"

class EdgarClientException(Exception):
    """Base exception for Edgar client errors."""
    pass

class MCPServerConnectionError(EdgarClientException):
    """Exception raised when MCP server connection fails."""
    def __init__(self, url: str, original_error: Exception = None):
        self.url = url
        self.original_error = original_error
        message = f"Cannot connect to MCP server at {url}"
        if original_error:
            message += f": {original_error}"
        super().__init__(message)

class EdgarClient:
    """Client for fetching and parsing SEC EDGAR filings."""
    
    def __init__(
        self, 
        mcp_server_url: Optional[str] = None,
        user_agent: str = DEFAULT_USER_AGENT,
        edgar_url: str = SEC_EDGAR_SEARCH_URL
    ):
        """Initialize the client.
        
        Args:
            mcp_server_url: URL for MCP browser automation server
                Defaults to MCP_SERVER_URL env var or http://localhost:3000
            user_agent: User agent header for SEC EDGAR requests
            edgar_url: SEC EDGAR search URL
            
        Example:
            >>> async with EdgarClient() as client:
            ...     status = await client.check_server_status()
            ...     if status["connected"]:
            ...         # Proceed with search and extraction
        """
        # Try environment variable if URL not provided
        self.mcp_server_url = mcp_server_url or os.environ.get(
            MCP_SERVER_URL_ENV, DEFAULT_MCP_SERVER_URL
        )
        self.edgar_url = edgar_url
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Referer": edgar_url
        }
        self.session: Optional[aiohttp.ClientSession] = None
        self.session_id: Optional[str] = None
        
        logger.info(f"EdgarClient initialized with MCP server at {self.mcp_server_url}")
        
    async def __aenter__(self):
        """Enable async context management."""
        logger.info("Creating aiohttp session")
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup session on exit."""
        logger.info("Closing client session")
        if self.session_id:
            try:
                await self._close_browser_session()
            except Exception as e:
                logger.warning(f"Error closing browser session: {e}")
        
        if self.session:
            await self.session.close()
        
        self.session = None
        self.session_id = None

    async def check_server_status(self) -> Dict[str, Any]:
        """Check if MCP server is running and available.
        
        Returns:
            Dictionary with server status information
            
        Example:
            >>> async with EdgarClient() as client:
            ...     status = await client.check_server_status()
            ...     print(f"MCP server connected: {status['connected']}")
        """
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.mcp_server_url}/status"
                logger.info(f"Checking MCP server status at {url}")
                
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"MCP server is running: {data}")
                        return {
                            "connected": True,
                            "version": data.get("version", "unknown"),
                            "status": "running"
                        }
                    else:
                        logger.warning(f"MCP server returned status {response.status}")
                        return {
                            "connected": False,
                            "status": "error",
                            "error": f"Server returned {response.status}"
                        }
            except aiohttp.ClientError as e:
                logger.warning(f"Failed to connect to MCP server: {e}")
                return {
                    "connected": False,
                    "status": "unavailable",
                    "error": str(e)
                }
            except Exception as e:
                logger.error(f"Unexpected error checking server status: {e}")
                return {
                    "connected": False,
                    "status": "error",
                    "error": str(e)
                }

    async def _create_session(self) -> str:
        """Create a new browser automation session.
        
        Returns:
            Session ID for the created browser session
            
        Raises:
            MCPServerConnectionError: If session creation fails
            RuntimeError: If client is not initialized
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async with.")
            
        try:
            logger.info(f"Creating browser session at {self.mcp_server_url}/session")
            
            async with self.session.post(
                f"{self.mcp_server_url}/session",
                headers=self.headers,
                json={"browserType": "chromium"}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Session creation failed: {response.status}, {error_text}")
                    raise MCPServerConnectionError(
                        self.mcp_server_url, 
                        Exception(f"Status {response.status}: {error_text}")
                    )
                
                data = await response.json()
                session_id = data.get("sessionId")
                
                if not session_id:
                    logger.error("No sessionId in response")
                    raise MCPServerConnectionError(
                        self.mcp_server_url, 
                        Exception("No sessionId in response")
                    )
                
                logger.info(f"Browser session created: {session_id}")
                return session_id
                
        except aiohttp.ClientError as e:
            logger.error(f"MCP server connection error: {e}")
            raise MCPServerConnectionError(self.mcp_server_url, e)
        except Exception as e:
            logger.error(f"Unexpected error creating session: {e}")
            raise MCPServerConnectionError(self.mcp_server_url, e)

    async def _close_browser_session(self) -> None:
        """Close the browser session on the MCP server."""
        if not self.session_id or not self.session:
            return
            
        try:
            logger.info(f"Closing browser session: {self.session_id}")
            
            async with self.session.delete(
                f"{self.mcp_server_url}/session/{self.session_id}",
                headers=self.headers
            ) as response:
                if response.status != 200:
                    logger.warning(f"Session close returned status {response.status}")
                else:
                    logger.info(f"Browser session closed: {self.session_id}")
        except Exception as e:
            logger.warning(f"Error closing browser session: {e}")

    async def navigate(self, url: str) -> bool:
        """Navigate the browser to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            bool: True if navigation was successful, False otherwise
                
        Raises:
            MCPServerConnectionError: If navigation fails
            RuntimeError: If no active session
        """
        if not self.session_id:
            self.session_id = await self._create_session()
            
        try:
            logger.info(f"Navigating to {url}")
            
            # Use the execute endpoint with navigate command instead of direct navigate endpoint
            async with self.session.post(
                f"{self.mcp_server_url}/session/{self.session_id}/execute",
                headers=self.headers,
                json={
                    "command": "navigate",
                    "args": {"url": url}
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Navigation failed: {response.status}, {error_text}")
                    return False
                
                logger.info(f"Successfully navigated to {url}")
                return True
                
        except aiohttp.ClientError as e:
            logger.error(f"Navigation failed due to connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during navigation: {e}")
            return False
        
    async def get_page_content(self) -> str:
        """Get the current page content.
        
        Returns:
            HTML content of the current page
            
        Raises:
            EdgarClientException: If content retrieval fails
        """
        if not self.session_id:
            self.session_id = await self._create_session()
            
        try:
            logger.info("Retrieving page content")
            
            async with self.session.get(
                f"{self.mcp_server_url}/session/{self.session_id}/content",
                headers=self.headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Content retrieval failed: {response.status}, {error_text}")
                    raise EdgarClientException(f"Content retrieval failed: {error_text}")
                
                content = await response.text()
                logger.info(f"Retrieved {len(content)} bytes of content")
                return content
                
        except aiohttp.ClientError as e:
            logger.error(f"Content retrieval failed due to connection error: {e}")
            raise EdgarClientException(f"Content retrieval failed: {e}")

    async def get_10k_metrics(
        self,
        cik: str,
        year: int,
        mock_data: Optional[Dict] = None
    ) -> FinancialStatementItems:
        """Get 10-K financial metrics for a fiscal year.
        
        Args:
            cik: Company CIK number (10 digits)
            year: Fiscal year to retrieve
            mock_data: Optional mock response for testing
        
        Returns:
            FinancialStatementItems: Validated filing metrics
            
        Raises:
            ValueError: If CIK is invalid
            ConnectionError: If MCP server request fails
        """
        if not cik.isdigit():
            raise ValueError("CIK must be numeric")
            
        if mock_data:
            logger.info(f"Using mock data for 10-K metrics (CIK: {cik}, year: {year})")
            return FinancialStatementItems.model_validate(mock_data)
            
        if not self.session_id:
            self.session_id = await self._create_session()
        
        # Prepare search parameters
        logger.info(f"Fetching 10-K metrics for CIK {cik}, year {year}")
        search_params = {
            "cik": cik,
            "form_type": "10-K",
            "fiscal_year": year
        }
        
        # Execute search via MCP browser automation
        try:
            async with self.session.post(
                f"{self.mcp_server_url}/session/{self.session_id}/execute",
                headers=self.headers,
                json=search_params
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"10-K metrics request failed: {response.status}, {error_text}")
                    raise ConnectionError(f"Failed to fetch 10-K metrics: {error_text}")
                
                logger.info(f"Successfully retrieved 10-K metrics for {cik}, {year}")
                data = await response.json()
                return FinancialStatementItems.model_validate(data)
        except aiohttp.ClientError as e:
            logger.error(f"10-K metrics request failed due to connection error: {e}")
            raise ConnectionError(f"Failed to fetch 10-K metrics: {e}")

    async def get_10q_metrics(
        self,
        cik: str,
        year: int,
        quarter: Literal["Q1", "Q2", "Q3", "Q4"],
        mock_data: Optional[Dict] = None
    ) -> FinancialStatementItems:
        """Get 10-Q financial metrics for a specific quarter.
            
        Args:
            cik: Company CIK number
            year: Fiscal year
            quarter: Fiscal quarter (Q1, Q2, Q3, Q4)
            mock_data: Optional mock response for testing
            
        Returns:
            FinancialStatementItems: Validated filing metrics
                
        Raises:
            ValueError: If CIK is invalid
            ConnectionError: If MCP server request fails
        """
        if not cik.isdigit():
            raise ValueError("CIK must be numeric")

        if mock_data:
            logger.info(f"Using mock data for 10-Q metrics (CIK: {cik}, {year} {quarter})")
            return FinancialStatementItems.model_validate(mock_data)
            
        if not self.session_id:
            self.session_id = await self._create_session()
        
        # Prepare search parameters
        logger.info(f"Fetching 10-Q metrics for CIK {cik}, {year} {quarter}")
        search_params = {
            "cik": cik,
            "form_type": "10-Q",
            "fiscal_year": year,
            "fiscal_quarter": quarter
        }
        
        # Execute search via MCP browser automation
        try:
            async with self.session.post(
                f"{self.mcp_server_url}/session/{self.session_id}/execute",
                headers=self.headers,
                json=search_params
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"10-Q metrics request failed: {response.status}, {error_text}")
                    raise ConnectionError(f"Failed to fetch 10-Q metrics: {error_text}")
                
                logger.info(f"Successfully retrieved 10-Q metrics for {cik}, {year} {quarter}")
                data = await response.json()
                return FinancialStatementItems.model_validate(data)
        except aiohttp.ClientError as e:
            logger.error(f"10-Q metrics request failed due to connection error: {e}")
            raise ConnectionError(f"Failed to fetch 10-Q metrics: {e}")

    async def get_company_financials(
        self, 
        cik: str,
        form_type: str,
        fiscal_period: FiscalPeriodType,
        year: int
    ) -> FinancialStatementItems:
        """Get company financials from SEC EDGAR.
        
        Args:
            cik: Company CIK (10 digits)
            form_type: 10-K or 10-Q
            fiscal_period: Annual or specific quarter
            year: Fiscal year
            
        Returns:
            Extracted financial metrics
            
        Example:
            >>> async with EdgarClient() as client:
            ...     # Get Tesla's 2024 Q1 financials
            ...     financials = await client.get_company_financials(
            ...         cik="0001318605",
            ...         form_type="10-Q",
            ...         fiscal_period="Q1",
            ...         year=2024
            ...     )
        """
        if form_type not in SUPPORTED_FORM_TYPES:
            raise ValueError(f"Form type must be one of {SUPPORTED_FORM_TYPES}")

        search = EdgarSearchCriteria(
            cik=cik,
            form_type=form_type,
            fiscal_year=year,
            fiscal_quarter=fiscal_period if form_type == "10-Q" else None
        )
        
        # TODO: Implement these helper methods
        filing = await self._search_filings(search)
        return await self._extract_financials(filing)