# indonesia-stocks-mcp 🏦

MCP server for **Indonesian stock fundamentals** via Yahoo Finance. Get financial statements, key metrics, prices, and dividends — all through `.JK` suffixed tickers.

## Quick Start

```bash
# Install & run (one command, no local data needed)
uvx indonesia-stocks-mcp
```

## Claude / Codex / Hermes Config

```json
{
  "mcpServers": {
    "indonesia-stocks": {
      "command": "uvx",
      "args": ["indonesia-stocks-mcp"]
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `get_stock_info` | Comprehensive stock overview: price, valuation (PE, PB, PEG), market cap, sector, analyst targets, beta, and more |
| `get_balance_sheet` | Balance sheet (neraca): assets, liabilities, equity — 40-50+ line items. Supports annual & quarterly. |
| `get_income_statement` | Income statement (laba rugi): revenue, gross profit, operating income, net income, EPS — 30+ line items |
| `get_cash_flow` | Cash flow (arus kas): operating/investing/financing activities, free cash flow, capex — 30+ line items |
| `get_key_metrics` | All key ratios in one call: ROE, ROA, margins, DER, CR, revenue/earnings growth, FCF, PE, PB, PEG, dividend yield |
| `get_current_price` | Quick price check with basic info |
| `get_historical_prices` | OHLCV historical data for charting |
| `get_dividend_history` | Dividend payout history |

## Data Sources

All data from **Yahoo Finance** using `.JK` suffix (JKT = Jakarta Stock Exchange). Covers all Indonesian stocks listed on IDX.

## Stock Codes

Use standard ticker codes (without .JK — added automatically):

```
BBRI    → Bank Rakyat Indonesia
BBCA    → Bank Central Asia
TLKM    → Telkom Indonesia
ASII    → Astra International
UNVR    → Unilever Indonesia
GOTO    → GoTo Gojek Tokopedia
ADRO    → Adaro Energy
ANTM    → Aneka Tambang
...
```

## Requirements

- Python >= 3.10
- Internet connection (data is fetched live, not stored locally)
