# SEC EDGAR Online Data Ingestion Component

A Python client for fetching financial metrics from SEC EDGAR filings (10K, 10Q reports, etc.) via MCP browser automation.
Part of the Charming Data Stock Market Trading project (May-June 2025).

## Integration Roadmap
- Uses [Browserbase MCP Server](https://github.com/browserbase/mcp-server-browserbase) for browser automation
- Leverages [Stagehand MCP Server](https://github.com/browserbase/mcp-server-browserbase/tree/main/stagehand) for DOM interactions
- Supports headless browser-based data extraction
- Ready for remote browser integration

## Technical Notes
"Remote browser" refers to:
- Browser instances running on the MCP server
- Headless Chrome/Firefox browsers
- Controlled via MCP Server's API
- Enables stateless web scraping

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
## Project Structure
```
.
├── src/
│   ├── edgar/             # Core implementation
│   │   ├── client.py     # Main client
│   │   └── session.py    # Session management
│   └── models/           # Data models
│       ├── company.py    # Company identifiers
│       └── metrics.py    # Financial metrics
├── examples/             # Usage examples
│   └── tesla_10k_scraper.py
├── tests/               # Test suite
└── MCP-SERVER-SEC-EDGAR-SCRAPING.md
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