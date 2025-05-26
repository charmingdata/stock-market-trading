"""Example script for fetching Tesla's financial metrics."""
import asyncio
import logging
from src.edgar.client import EdgarClient
from src.edgar.models.financial_statement_items import EdgarMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Fetch Tesla's latest financial metrics from SEC EDGAR."""
    try:
        async with EdgarClient() as client:
            logger.info("Fetching Tesla financials...")
            metrics = await client.get_tesla_financials()
            logger.info(f"Tesla Metrics: {metrics}")
    except Exception as e:
        logger.error(f"Failed to fetch metrics: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    