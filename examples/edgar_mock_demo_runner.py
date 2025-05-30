"""
MCP Server Status and SEC EDGAR Financial Data Extraction Demo

This script demonstrates:
1. MCP server connection testing
2. SEC EDGAR navigation
3. Tesla 10-K financial data extraction

Usage:
    python3 examples/edgar_mock_demo_runner.py [--server-url URL] [--extract-data] [--mock]
"""
import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Import from the package
from src.edgar.client.client import EdgarClient
from examples.edgar_mock_demo.mcp_server_checker import check_mcp_server
from examples.edgar_mock_demo.sec_navigator_mock import search_tesla_10k_filing
from examples.edgar_mock_demo.data_simulator import simulate_financial_data
from examples.edgar_mock_demo.data_display import display_financial_data, save_financial_data
from examples.edgar_mock_demo.mock_client import MockEdgarClient 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def run_demo(server_url=None, extract_data=False, mock_mode=False):
    """Run the full demo with connection check and optional data extraction."""
    # Use mock client if mock mode is enabled
    if mock_mode:
        print("\n📄 Running in mock mode (no MCP server required)")
        client = MockEdgarClient(mcp_server_url=server_url)
        
        async with client:
            # Search for Tesla's latest 10-K filing
            filing = await search_tesla_10k_filing(client)
            
            if filing:
                # Extract financial data from the filing
                financial_data = await simulate_financial_data(client, filing)
                
                # Display the extracted data
                display_financial_data(financial_data)
                
                # Save the data to a JSON file for reference
                output_path = save_financial_data(financial_data, current_dir)
                print(f"\nData saved to {output_path}")
        
        return
    
    # Check MCP server connection if not in mock mode
    connection_ok = await check_mcp_server(server_url)
    
    if connection_ok and extract_data:
        client = EdgarClient(mcp_server_url=server_url)
        
        async with client:
            # Search for Tesla's latest 10-K filing
            filing = await search_tesla_10k_filing(client)
            
            if filing:
                # Extract financial data from the filing
                financial_data = await simulate_financial_data(client, filing)
                
                # Display the extracted data
                display_financial_data(financial_data)
                
                # Save the data to a JSON file for reference
                output_path = save_financial_data(financial_data, current_dir)
                print(f"\nData saved to {output_path}")
    elif not connection_ok and extract_data:
        print("\n❓ Would you like to continue in mock mode? (y/n)")
        response = input().strip().lower()
        if response == 'y':
            # Run the demo again in mock mode
            await run_demo(server_url, extract_data, mock_mode=True)

def parse_args():
    parser = argparse.ArgumentParser(description="MCP server and SEC EDGAR data extraction demo")
    parser.add_argument(
        "--server-url",
        help="MCP server URL (default: uses MCP_SERVER_URL env var or http://localhost:3000)",
        default=None
    )
    parser.add_argument(
        "--extract-data",
        help="Extract Tesla financial data after connection check",
        action="store_true"
    )
    parser.add_argument(
        "--mock",
        help="Run in mock mode without requiring real MCP server connection",
        action="store_true"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(run_demo(args.server_url, args.extract_data, args.mock))