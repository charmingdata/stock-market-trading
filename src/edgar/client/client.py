"""SEC EDGAR API client for fetching financial metrics via MCP browser automation."""
import aiohttp
import os
import logging
import uuid
from typing import Optional, Dict, Literal, Any

from .session import check_server_status
from .filing_access import get_company_filings, _get_filing_url
from .exceptions import MCPServerConnectionError
from .scraper import EdgarScraper   
from .search_params import _search_filings
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
        
        # Validate CIK
        if not cik.isdigit() or len(cik) != 10:
            raise ValueError("CIK must be a 10-digit numeric string")
        if not self.session_id:
            self.session_id = await self._create_session()
        # Navigate to EDGAR search page
        edgar_search_url = f"{self.edgar_url}/search"
        if not await self.navigate(edgar_search_url):
            raise MCPServerConnectionError(self.mcp_server_url, "Failed to navigate to EDGAR search page")
        # Perform search and extract financials
        logger.info(f"Searching for {form_type} filings for CIK {cik}, year {year}, period {fiscal_period}")
        # Note: The actual search and extraction logic would depend on the MCP server's capabilities
        # This is a placeholder for the actual search and extraction logic
        filing = await _search_filings(search)
        if not filing:
            raise ValueError(f"No filings found for CIK {cik}, form type {form_type}, year {year}")
        financials = await _extract_financials(filing)
        if not financials:
            raise ValueError(f"No financial metrics found for CIK {cik}, form type {form_type}, year {year}")
        logger.info(f"Successfully extracted financials for CIK {cik}, form type {form_type}, year {year}")
        return financials
    