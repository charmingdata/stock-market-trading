import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.edgar_client import EdgarClient

async def main():
    # Initialize client
    client = EdgarClient()
    
    # Test Tesla's Q1 2025 10-Q filing
    metrics = await client.get_latest_10q_metrics(cik="1318605")
    
    print("\nTesla's Latest 10-Q Metrics:")
    print(f"Session ID: {client.session_id}")
    print("Response:", metrics)

if __name__ == "__main__":
    asyncio.run(main())