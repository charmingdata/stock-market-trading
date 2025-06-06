"""Mock client implementation for demos without MCP server."""

class MockEdgarClient:
    """Mock client for when MCP server is unavailable."""
    
    def __init__(self, **kwargs):
        """Initialize with mock mode enabled."""
        self.mock_mode = True
        self.session_id = "mock-session"
        self.mcp_server_url = kwargs.get("mcp_server_url", "http://mock-server")
        
    async def __aenter__(self):
        """Enter async context."""
        print("📄 MOCK: Creating browser session")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        print("📄 MOCK: Closing browser session")
        
    async def navigate(self, url):
        """Mock navigation."""
        print(f"📄 MOCK: Navigating to {url}")
        return True
    
    async def get_page_content(self):
        """Mock content retrieval."""
        print("📄 MOCK: Retrieving page content")
        return "<html><body><h1>Mock Tesla Financial Data</h1></body></html>"
    