"""Demo script for extracting Tesla's income statement from latest 10-K.

NOTE: This is a placeholder that will be implemented in the next PR.
This file shows the planned API structure and usage.
"""
import asyncio
from edgar.client import EdgarClient

async def extract_tesla_income_statement():
    """Extract Tesla's income statement from latest 10-K filing."""
    print("Starting Tesla income statement extraction demo...")
    
    async with EdgarClient() as client:
        # This will be implemented in next PR
        financials = await client.get_10k_metrics(
            cik="0001318605",  # Tesla's CIK
            year=2024
        )
        
        print("\nTesla Income Statement Highlights:")
        print(f"Revenue: ${financials.revenue}")
        print(f"Operating Income: ${financials.operating_income}")
        print(f"Net Income: ${financials.net_income}")
        print(f"EPS (Basic): ${financials.eps_basic}")
        print(f"EPS (Diluted): ${financials.eps_diluted}")

if __name__ == "__main__":
    print("To run this demo:")
    print("1. Start MCP server in another terminal: cd ../mcp-server-browserbase && npm start")
    print("2. Implementation coming in next PR\n")
    print("This file shows the planned API structure for Tesla income statement extraction.")
