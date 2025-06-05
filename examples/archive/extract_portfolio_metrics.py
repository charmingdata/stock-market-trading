import asyncio
import pandas as pd
from src.edgar_client import EdgarClient

async def main():
    # Sample of 3 companies from portfolio for demo
    portfolio_ciks = [
        "1318605",  # Tesla
        "0000320193",  # Apple
        "1652044"  # Alphabet
    ]
    
    client = EdgarClient()
    results = []
    
    for cik in portfolio_ciks:
        metrics = await client.get_latest_10q_metrics(cik)
        if metrics:
            results.append(metrics)
    
    # Convert to DataFrame for team's data visualization
    df = pd.DataFrame(results)
    print(df.to_string())
    
    # Save for other team members
    df.to_csv('latest_10q_metrics.csv', index=False)

if __name__ == "__main__":
    asyncio.run(main())