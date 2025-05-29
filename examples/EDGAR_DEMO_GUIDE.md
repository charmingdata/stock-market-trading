# SEC EDGAR Demo Examples Guide

This guide covers the example scripts in this directory, focusing on the simulation demo that shows the intended architecture. These examples are separate from the main project implementation.

## Demo Scripts

### Current Development Demo
- `edgar_data_simulation.py` - Demonstrates the architecture with simulated data extraction

### Package Structure
- `edgar_mock_demo/` - Modules for the simulation demo
  - `mcp_server_checker.py` - Real MCP server connection testing
  - `sec_navigator_mock.py` - Simulated SEC EDGAR navigation
  - `data_simulator.py` - Simulated financial data extraction
  - `data_display.py` - Display and formatting utilities
  - `mock_client.py` - Mock client implementation

### Previous Examples
- `edgar_client_mcp_server.py` - Basic MCP server interaction
- `edgar_client_extract_financial_statements.py` - Example extraction logic

## Usage

```bash
# Run the simulation demo with MCP server check:
python3 edgar_data_simulation.py --extract-data

# Run in full mock mode (no MCP server needed):
python3 edgar_data_simulation.py --mock --extract-data