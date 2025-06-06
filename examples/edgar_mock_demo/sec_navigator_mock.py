"""SEC EDGAR navigation functions."""
import logging
from typing import Dict, Any, Optional

# Tesla company info
TESLA_CIK = "0001318605"
TESLA_TICKER = "TSLA"
TESLA_NAME = "Tesla, Inc."

logger = logging.getLogger(__name__)

async def search_tesla_10k_filing(client) -> Optional[Dict[str, Any]]:
    """Search for Tesla's latest 10-K filing."""
    print("\n===== Tesla 10-K Filing Search =====\n")
    
    # Use mock data if we can't navigate
    if hasattr(client, 'mock_mode') and client.mock_mode:
        print("📄 Using mock filing data for Tesla...")
        return get_mock_tesla_filing()
    
    search_url = "https://www.sec.gov/edgar/search/#/category=custom&entityName=tesla"
    
    try:
        # Navigate to SEC search for Tesla
        print(f"🔍 Navigating to SEC EDGAR search for {TESLA_NAME}...")
        await client.navigate(search_url)
        
        # For demo, we'll use a direct filing URL instead of searching
        latest_10k_url = "https://www.sec.gov/ix?doc=/Archives/edgar/data/1318605/000095017023001409/tsla-20221231.htm"
        print(f"🔍 Navigating to Tesla's latest 10-K filing...")
        await client.navigate(latest_10k_url)
        
        # Get the filing content
        print("🔍 Retrieving filing content...")
        content = await client.get_page_content()
        
        print(f"✅ Successfully retrieved Tesla's 10-K filing ({len(content)} bytes)")
        
        return {
            "company": TESLA_NAME,
            "cik": TESLA_CIK,
            "ticker": TESLA_TICKER,
            "form_type": "10-K",
            "filing_date": "2023-01-31",
            "period_end": "2022-12-31",
            "url": latest_10k_url
        }
    except Exception as e:
        print(f"❌ Error searching for Tesla's 10-K filing: {e}")
        print("📄 Falling back to mock filing data...")
        return get_mock_tesla_filing()

def get_mock_tesla_filing():
    """Return mock Tesla filing data for demo purposes."""
    return {
        "company": "Tesla, Inc.",
        "cik": "0001318605",
        "ticker": "TSLA",
        "form_type": "10-K",
        "filing_date": "2023-01-31",
        "period_end": "2022-12-31",
        "url": "https://www.sec.gov/ix?doc=/Archives/edgar/data/1318605/000095017023001409/tsla-20221231.htm",
        "mock": True
    }