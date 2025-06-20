class EdgarClientException(Exception):
    """Base exception for Edgar client errors."""

class MCPServerConnectionError(EdgarClientException):
    """Exception raised when MCP server connection fails."""
    def __init__(self, url: str, original_error: Exception = None):
        self.url = url
        self.original_error = original_error
        message = f"Cannot connect to MCP server at {url}"
        if original_error:
            message += f": {original_error}"
        super().__init__(message)
