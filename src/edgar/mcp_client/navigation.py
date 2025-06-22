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
