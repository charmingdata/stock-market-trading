import sys
import os
import asyncio
import logging
import traceback

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.edgar.client import EdgarClient
from src.models.company import CompanyIdentifier

async def scrape_tesla_10k():
    """Scrape Tesla's latest 10-K filing and extract metrics."""
    tesla = CompanyIdentifier(
        cik="1318605",
        company_name="Tesla, Inc."
    )
    
    async with EdgarClient() as client:
        try:
            filing = await client.find_latest_filing(
                cik=tesla.cik,
                form_type="10-K"
            )
            
            metrics = await client.extract_filing_metrics(
                document_url=filing.document_url,
                cik=tesla.cik
            )
            
            print(f"Tesla's Latest 10-K Metrics:")
            print(f"Filing Date: {filing.filing_date}")
            print(f"Revenue: {metrics.revenue}")
            print(f"Net Income: {metrics.net_income}")
            print(f"EPS (Basic): {metrics.eps_basic}")
            
        except Exception as e:
            print(f"Error scraping Tesla 10-K: {e}")
            print("\nTraceback:")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(scrape_tesla_10k())