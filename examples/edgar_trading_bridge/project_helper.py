"""
Project-specific helpers for the SEC EDGAR trading bridge.

This module contains constants, utility functions, and documentation helpers
specific to the project integration.
"""

import os

# Company watchlist for analysis
COMPANY_WATCHLIST = [
    {"symbol": "TSLA", "cik": "0001318605", "name": "Tesla Inc"},
    {"symbol": "AAPL", "cik": "0000320193", "name": "Apple Inc"},
    {"symbol": "MSFT", "cik": "0000789019", "name": "Microsoft Corp"},
    {"symbol": "GOOGL", "cik": "0001652044", "name": "Alphabet Inc"},
    {"symbol": "AMZN", "cik": "0001018724", "name": "Amazon.com Inc"},
]

def print_project_alignment():
    """Print information about how this script aligns with project goals."""
    print("\n===== Project Alignment Information =====\n")
    print("This script bridges the SEC EDGAR data extraction with project trading strategies.")
    print("It demonstrates the following connections to project components:")
    print()
    print("1. a1_simulate_trades.py Integration")
    print("   - Converts financial metrics to trading signals")
    print("   - Uses similar signal format (BUY, SELL, HOLD)")
    print("   - Can be extended to call a1_simulate_trades.py functions directly")
    print()
    print("2. a2_standardize_executed_trades.py Connection")
    print("   - Produces standardized financial data")
    print("   - Can feed into the trade standardization process")
    print("   - Saved CSV follows similar structure for compatibility")
    print()
    print("3. a3_analysis.py Preparation")
    print("   - Generates data that can be analyzed with a3_analysis.py")
    print("   - Includes key metrics for performance evaluation")
    print()
    print("Team Feedback Requested:")
    print("- Which additional financial metrics would be valuable for your strategies?")
    print("- Are there specific fiscal periods that are more relevant for analysis?")
    print("- What trading signal thresholds work best with the existing strategies?")
    print()
    print("To provide feedback, add comments to the project tracking document")
    print("or create a branch with your suggested modifications.")

