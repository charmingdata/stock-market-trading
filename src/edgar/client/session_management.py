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

async def _create_session(self) -> str:
    """Generate a new session ID for Browserbase MCP server."""
    session_id = str(uuid.uuid4())
    logger.info(f"Generated new session ID: {session_id}")
    return session_id    

async def _close_browser_session(self) -> None:
        """Close the browser session on the MCP server."""
        if not self.session_id:
            logger.warning("No active session to close")
            return
        
        try:
            logger.info(f"Closing browser session {self.session_id}")
            async with self.session.post(
                f"{self.mcp_server_url}/session/{self.session_id}/close",
                headers=self.headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to close session: {response.status}, {error_text}")
                else:
                    logger.info(f"Successfully closed session {self.session_id}")
        except aiohttp.ClientError as e:
            logger.error(f"Error closing session: {e}")
        finally:
            self.session_id = None


    