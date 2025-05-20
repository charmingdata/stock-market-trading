"""Basic Tesla 10-K scraper demonstrating core functionality."""

import asyncio
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_tesla_10k():
    """Fetch Tesla's latest 10-K filing using mock data."""
    logger.info("Fetching Tesla 10-K filing...")
    
    # Mock successful response for initial testing
    filing = {
        "cik": "1318605",
        "company": "Tesla, Inc.",
        "form": "10-K",
        "date": datetime.now().isoformat(),
        "status": "success",
        "metrics": {
            "revenue": "$81.4B",
            "net_income": "$12.6B",
            "eps": "3.63"
        }
    }
    
    return filing

async def main():
    try:
        result = await fetch_tesla_10k()
        print("\nTesla 10-K Filing:")
        print(f"Company: {result['company']}")
        print(f"Form: {result['form']}")
        print(f"Date: {result['date']}")
        print("\nKey Metrics:")
        print(f"Revenue: {result['metrics']['revenue']}")
        print(f"Net Income: {result['metrics']['net_income']}")
        print(f"EPS: {result['metrics']['eps']}")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())