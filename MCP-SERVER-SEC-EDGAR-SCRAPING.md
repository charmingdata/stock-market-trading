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
from src.edgar.client import EdgarClient
from src.models.company import CompanyIdentifier

async def main():
    tesla = CompanyIdentifier(
        cik="1318605",
        company_name="Tesla, Inc."
    )
    
    async with EdgarClient() as client:
        filing = await client.find_latest_filing(
            cik=tesla.cik,
            form_type="10-K"
        )
        print(f"Latest 10-K: {filing}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

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
- Project structure reorganized and documented
- Basic models implemented with Pydantic
- Test imports fixed per reviewer feedback
- MVP implementation with mock responses
- Basic test coverage for data validation
- Ready for MCP server integration

## Next Steps
- Implement edgar client functionality
  - Live scraping via MCP server
  - XBRL parsing for metrics
  - SEC rate limiting
- Add comprehensive test coverage
- Set up CI/CD pipeline
- Add historical data support