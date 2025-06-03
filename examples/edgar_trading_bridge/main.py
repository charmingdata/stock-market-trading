"""
Main entry point for the SEC EDGAR trading bridge.

This module contains the main function and CLI handling for the integration bridge
between SEC EDGAR data extraction and trading strategies.
"""

import asyncio
import logging
import argparse
import os
import sys
from typing import Dict, List, Optional

# Add src directory to path
sys.path.append(
    (os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))))

from src.edgar.client.client import EdgarClient
from src.edgar.models import FinancialStatementItems

from .data_fetcher import fetch_company_financial_data
from .data_processor import financial_metrics_to_df
# Import from strategies instead of data_processor
from .strategies import apply_simple_trading_strategy
from .project_helper import print_project_alignment, COMPANY_WATCHLIST

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main(mock_mode=True):
    """Main execution function."""
    # Set up MCP server URL (or use mock mode)
    server_url = None
    if not mock_mode:
        server_url = os.environ.get("MCP_SERVER_URL", "http://localhost:3000")
    
    # Create client
    client = EdgarClient(mcp_server_url=server_url)
    
    # Year to analyze
    analysis_year = 2024
    
    try:
        # Collect all financial data
        all_financial_data = []
        
        for company in COMPANY_WATCHLIST:
            logger.info(f"Processing {company['name']} ({company['symbol']})")
            company_data = await fetch_company_financial_data(
                client, company, analysis_year, mock_mode
            )
            all_financial_data.extend(company_data)
        
        # Convert to DataFrame
        financial_df = financial_metrics_to_df(all_financial_data)
        
        # Apply trading strategy
        results_df = apply_simple_trading_strategy(financial_df)
        
        # Save results
        results_df.to_csv("financial_trading_analysis.csv", index=False)
        
        # Display summary
        print("\n===== Financial Trading Analysis =====\n")
        for symbol, group in results_df.groupby('symbol'):
            print(f"{symbol} ({group['company_name'].iloc[0]})")
            print("─" * 50)
            
            for _, row in group.iterrows():
                print(f"{row['period']}: Revenue ${row['revenue']/1e9:.1f}B, "
                      f"Op. Margin {row['operating_margin']:.1%}, "
                      f"Signal: {row['trading_signal']}")
            print()
        
        print(f"Full results saved to financial_trading_analysis.csv")
        
        # Print project alignment information
        print_project_alignment()

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

def run_cli():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(
        description="SEC EDGAR Trading Integration Example"
    )
    parser.add_argument(
        "--live", action="store_true", 
        help="Use live SEC EDGAR data instead of mock data"
    )
    
    args = parser.parse_args()
    asyncio.run(main(mock_mode=not args.live))

if __name__ == "__main__":
    run_cli()