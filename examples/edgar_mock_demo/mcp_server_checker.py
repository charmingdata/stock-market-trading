"""MCP server connectivity testing."""
import aiohttp
import logging
import os
from typing import Dict, Any, Optional

# Root logger
logger = logging.getLogger(__name__)

# Constants for MCP server configuration
MCP_SERVER_URL_ENV = "MCP_SERVER_URL"
DEFAULT_MCP_SERVER_URL = "http://localhost:3000"

async def check_mcp_server(server_url=None):
    """Check if MCP server is running and provide connection details."""
    # Get server URL from argument, environment, or default
    mcp_server_url = server_url or os.environ.get(MCP_SERVER_URL_ENV, DEFAULT_MCP_SERVER_URL)
    
    print("\n===== MCP Server Status Check =====\n")
    
    # Try root endpoint
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{mcp_server_url}/"
            print(f"🔍 Checking MCP server at {url}...")
            
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    print(f"✅ MCP Server is RUNNING at {mcp_server_url}")
                    
                    # Check /session endpoint (for creating browser sessions)
                    session_endpoint_ok = await check_session_endpoint(session, mcp_server_url)
                    
                    if session_endpoint_ok:
                        print("\n✅ MCP server session creation is available")
                        return True
                    else:
                        print("\n❌ MCP server is running but session creation failed")
                        print_troubleshooting_info(mcp_server_url)
                        return False
                else:
                    print(f"❌ MCP server returned status {response.status}")
                    print_troubleshooting_info(mcp_server_url)
                    return False
        except Exception as e:
            print(f"❌ Cannot connect to MCP server: {e}")
            print_troubleshooting_info(mcp_server_url)
            return False

async def check_session_endpoint(session, server_url):
    """Check if the /session endpoint is working."""
    try:
        print(f"🔍 Testing session creation at {server_url}/session...")
        
        # Test with a minimal payload
        async with session.post(
            f"{server_url}/session",
            json={"browserType": "chromium"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                session_id = data.get("sessionId")
                
                if session_id:
                    print(f"✅ Successfully created test session: {session_id}")
                    
                    # Clean up by closing the session
                    await close_test_session(session, server_url, session_id)
                    return True
                else:
                    print("❌ Session creation response missing sessionId")
                    return False
            else:
                print(f"❌ Session creation failed with status {response.status}")
                return False
    except Exception as e:
        print(f"❌ Error testing session endpoint: {e}")
        return False

async def close_test_session(session, server_url, session_id):
    """Close a test browser session."""
    try:
        print(f"🔍 Closing test session {session_id}...")
        
        async with session.delete(
            f"{server_url}/session/{session_id}"
        ) as response:
            if response.status == 200:
                print("✅ Successfully closed test session")
            else:
                print(f"⚠️ Session close returned status {response.status}")
    except Exception as e:
        print(f"⚠️ Error closing test session: {e}")

def print_troubleshooting_info(server_url):
    """Print troubleshooting information for connection issues."""
    print("\n🔧 TROUBLESHOOTING:")
    print("1. Is the MCP server running? Start it with:")
    print("   cd ../mcp-server-browserbase && npm start")
    print("\n2. Check the server URL:")
    print(f"   Current URL: {server_url}")
    print("   You can set MCP_SERVER_URL environment variable or use --server-url")
    print("\n3. Check for firewall or port issues:")
    print("   Make sure port 3000 (or your custom port) is accessible")
    print("\n4. Look for errors in the MCP server logs")
    print("\n5. Verify MCP server API endpoints:")
    print("   The server should respond to POST /session for creating a browser session")