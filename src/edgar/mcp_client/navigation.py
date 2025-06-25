import logging
import aiohttp
import socket
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class EdgarClientException(Exception):
    pass

class MCPServerConnectionError(Exception):
    pass

class MCPClient:
    # ... other methods and initialization ...
    
    @staticmethod
    def _is_url_allowed(url: str) -> bool:
        """
        Validates that the URL is allowed for navigation.
        Returns True if allowed, False if not allowed.
        """
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if hostname is None:
            return False
        # Deny-list of hostnames and addresses commonly abused for SSRF
        deny_list = {
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "169.254.169.254",
            "::1",
            "ip6-localhost",
            "ip6-loopback"
        }
        if hostname in deny_list:
            return False
        try:
            # Try to resolve to IP address (IPv4 or IPv6)
            addr = socket.gethostbyname(hostname)
            octets = addr.split('.')
            # Block RFC1918/private/reserved ranges and link-local, loopback
            if (
                addr.startswith("10.") or
                addr.startswith("127.") or
                addr.startswith("169.254.") or
                addr.startswith("172.") and 16 <= int(octets[1]) <= 31 or
                addr.startswith("192.168.") or
                addr == "0.0.0.0"
            ):
                return False
            # Optionally, expand to block more reserved ranges as needed
        except Exception:
            # If resolution fails, better to be safe and reject
            return False
        return True
    
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

        # Validate the URL before proceeding to prevent SSRF
        if not self._is_url_allowed(url):
            logger.error(f"Navigation blocked for disallowed or unsafe URL: {url}")
            return False

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
        """Get the current page content using the execute command.
        
        Returns:
            HTML content of the current page
            
        Raises:
            EdgarClientException: If content retrieval fails
        """
        if not self.session_id:
            self.session_id = await self._create_session()

        try:
            logger.info("Retrieving page content via execute command")
            async with self.session.post(
                f"{self.mcp_server_url}/session/{self.session_id}/execute",
                headers=self.headers,
                json={"command": "content"}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Content retrieval failed: {response.status}, {error_text}")
                    raise EdgarClientException(f"Content retrieval failed: {error_text}")
                data = await response.json()
                content = data.get("content", "")
                logger.info(f"Retrieved {len(content)} bytes of content")
                return content
        except aiohttp.ClientError as e:
            logger.error(f"Content retrieval failed due to connection error: {e}")
            raise EdgarClientException(f"Content retrieval failed: {e}")