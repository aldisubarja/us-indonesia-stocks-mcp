# 🇮🇩 Indonesia Stocks MCP

**MCP server** for Indonesian stock fundamental data — income statement, balance sheet, cash flow, and ratios from **RTI** and official **IDX InlineXBRL** filings, plus real-time prices from **Yahoo Finance**.

## Tools

### Yahoo Finance (live — no local data needed)
| Tool | Description |
|------|-------------|
| `get_current_price` | Latest stock price + market cap, PE, dividend yield |
| `get_historical_prices` | OHLCV historical data |

### RTI (local HTML data)
| Tool | Description |
|------|-------------|
| `rti_get_general_info` | Company: name, listed date, shares, board, currency |
| `rti_get_income_statement` | Full P&L — 27 fields (sales → net income → EPS) |
| `rti_get_balance_sheet` | Balance sheet — 25 fields (assets, liabilities, equity) |
| `rti_get_cash_flow` | Cash flow — 17 fields (operating, investing, financing) |
| `rti_get_ratios` | EPS, PER, ROE, NPM, PBV |

### IDX InlineXBRL (local extracted HTML)
| Tool | Description |
|------|-------------|
| `idx_get_general_info` | Official IDX company filings |
| `idx_get_balance_sheet` | Official IDX balance sheet |

### Utility
| Tool | Description |
|------|-------------|
| `list_available_data` | Scan `STOCKS_DATA_DIR` for available stocks and periods |

## Installation

### Prerequisites
- Python 3.10+
- `uv` (recommended) or `pip`

### Quick Start

```bash
# Clone
git clone https://github.com/aldisubarja/indonesia-stocks-mcp.git
cd indonesia-stocks-mcp

# Install with uv
uv pip install -e .

# Or with pip
pip install -e .
```

### Configure Hermes Agent

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  idn-stocks:
    command: "uv"
    args: ["run", "--directory", "/path/to/indonesia-stocks-mcp", "indonesia-stocks-mcp"]
    env:
      STOCKS_DATA_DIR: "/home/user/saham"
```

Then restart Hermes Agent. Tools appear as `mcp_idn_stocks_*`.

## Data Directory Structure

Set `STOCKS_DATA_DIR` environment variable (default: `~/saham`).

```
$STOCKS_DATA_DIR/
├── idx/                              # IDX InlineXBRL data
│   └── {year}/Q{quarter}/{code}/
│       └── inlineXBRL/               # extracted ZIP contents
│           ├── GeneralInfo.html
│           ├── BalanceSheet.html
│           └── IncomeStatement.html
│
└── rti/                              # RTI data
    ├── daftar_saham.xlsx             # stock list from IDX
    ├── income_statement/
    │   └── {end_period}/{period}/{code}.html
    ├── balance_sheet/
    │   └── {end_period}/{period}/{code}.html
    └── cash_flow/
        └── {end_period}/{period}/{code}.html
```

### Getting Data

This MCP server **reads** local data — it does NOT scrape. Use the upstream scraper to download:

```bash
git clone https://github.com/basnugroho/indonesia-stocks-scraper
# Follow instructions to download RTI + IDX data
# Point STOCKS_DATA_DIR to your download directory
```

## Example Usage

After connecting to Hermes:

> "Get BBRI's latest financial ratios and income statement"

The agent will call:
1. `mcp_idn_stocks_rti_get_income_statement(stock_code="BBRI", period="annual")`
2. `mcp_idn_stocks_rti_get_ratios(stock_code="BBRI")`

## License

MIT
