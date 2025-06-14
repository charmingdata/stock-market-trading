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

### Browser Automation Options

#### Current: Browserbase MCP
- Basic browser automation
- Local development friendly
- Simple setup process
- Good for MVP development
- Core team familiarity
- Zero cost barrier

#### Alternative: Bright Data MCP
- Enterprise-grade solution
- Built-in XBRL parsing
- Anti-blocking features
- Better for production use
- Higher cost barrier
- New learning curve

Note: Initial development focuses on Browserbase MCP. Bright Data consideration deferred to production phase.

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

### Environment Setup
```bash
# Create virtual environment
python3 -m venv ../.venv_sec_edgar
source ../.venv_sec_edgar/bin/activate

# Install dependencies
pip3 install -r requirements.txt
```

### MCP Server Setup
```bash
# Clone MCP server if not already done
git clone https://github.com/browserbase/mcp-server-browserbase.git ../mcp-server-browserbase

# Install Node.js dependencies
cd ../mcp-server-browserbase
npm install  # First time only

# Start server
npm start    # Runs on http://localhost:3000
```

### Running Tests
```bash
# From project root (recommended)
python -m pytest tests/ -v

# From tests directory
cd tests/
python -m pytest -v

# With specific test file
python -m pytest tests/test_edgar_client.py -v
```

### Path Configuration
Tests automatically add project root to Python path. For development:
```bash
# Option 1: Set PYTHONPATH (persistent)
export PYTHONPATH="${PYTHONPATH}:/path/to/project"

# Option 2: Use VSCode settings (recommended)
# In .vscode/settings.json:
{
    "python.envFile": "${workspaceFolder}/.env",
    "python.analysis.extraPaths": ["${workspaceFolder}"]
}
```

### Development Workflow
1. Start MCP server in separate terminal
2. Activate virtual environment
3. Run tests to verify setup
4. Make code changes
5. Run specific test file during development
6. Run full test suite before committing

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

## Notes
- Current focus on Browserbase MCP integration
- Production scaling options to be evaluated
- Alternative tools considered after MVP