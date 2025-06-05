import aiohttp
import logging
from typing import Dict, Any

async def check_server_status() -> Dict[str, Any]:
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
                url = f"{mcp_server_url}/status"
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