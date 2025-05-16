# SEC EDGAR Data Ingestion Component

A Python client for fetching financial metrics from SEC EDGAR filings via MCP browser automation.
Part of the Charming Data Stock Market Trading project (May-June 2025).

## Features
- Pydantic models for SEC filing validation
- Async client for EDGAR API integration
- Mock implementation for initial testing
- Ready for MCP browser automation

## Installation

```bash
# Create virtual environment
python3 -m venv ../.venv_sec_edgar
source ../.venv_sec_edgar/bin/activate

# Install dependencies
pip3 install -r requirements.txt
```

## Usage

```python
from src.edgar_client import EdgarClient

async def main():
    client = EdgarClient()
    metrics = await client.get_latest_10q_metrics(cik="1318605")  # Tesla
    print(metrics)

if __name__ == "__main__":
    asyncio.run(main())
```

## Project Structure
```
.
├── src/
│   ├── edgar_client.py    # Main client implementation
│   └── models/
│       └── filing.py      # SEC filing data models
├── tests/
│   └── test_edgar_client.py
├── pytest.ini             # Test configuration
└── requirements.txt       # Project dependencies
```

## Development

```bash
# Run tests
python3 -m pytest tests/ -v

# Start MCP server (required for live data)
cd ../mcp-server-browserbase
npm start
```

## Current Status
- MVP implementation with mock data responses
- Basic test coverage for data validation
- Ready for MCP server integration

## Next Steps
- Integrate with MCP server for live scraping
- Add XBRL parsing for actual metrics
- Implement SEC rate limiting
- Add historical data support