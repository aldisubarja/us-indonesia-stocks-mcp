# us-indonesia-stocks-mcp 🇺🇸🇮🇩📈

MCP server for **US and Indonesian stock data** via Yahoo Finance. Get financial statements, key metrics, prices, historical OHLCV, and dividends.

## Quick Start

```bash
# Install & run (one command, no local data needed)
uvx us-indonesia-stocks-mcp
```

## Claude / Codex / Hermes Config

```json
{
  "mcpServers": {
    "us-indonesia-stocks": {
      "command": "uvx",
      "args": ["us-indonesia-stocks-mcp"]
    }
  }
}
```

## Available Tools

- `get_stock_info` — comprehensive stock overview: price, valuation (PE, PB, PEG), market cap, sector, analyst targets, beta, and more
- `get_balance_sheet` — balance sheet (neraca): assets, liabilities, equity; annual or quarterly
- `get_income_statement` — income statement (laba rugi): revenue, gross profit, operating income, net income, EPS
- `get_cash_flow` — cash flow (arus kas): operating/investing/financing, free cash flow, capex
- `get_key_metrics` — key ratios: ROE, ROA, margins, DER, CR, revenue/earnings growth, FCF, PE, PB, PEG, dividend yield
- `get_current_price` — quick price check with basic info
- `get_historical_prices` — OHLCV historical data for charting / backtesting
- `get_dividend_history` — dividend payout history

## Market Support

Pass `market` in every tool call:

- `market="ID"` → Indonesian stocks, automatically adds `.JK`
- `market="US"` → US stocks, uses ticker as-is

Default is `ID` for backward compatibility.

## Examples

### Indonesian stocks

```json
{"stock_code": "BBRI", "market": "ID"}
```

Resolves to `BBRI.JK`

### US stocks

```json
{"stock_code": "AAPL", "market": "US"}
```

Resolves to `AAPL`

### Historical daily prices

```json
{
  "stock_code": "SPY",
  "market": "US",
  "start_date": "2020-01-01",
  "end_date": "2025-01-01",
  "interval": "1d"
}
```

## Notes

- Data source: **Yahoo Finance**
- Indonesian stocks use Yahoo suffix `.JK`
- US stocks use plain tickers like `AAPL`, `MSFT`, `SPY`, `NVDA`
- Data availability depends on Yahoo Finance coverage
- Historical intervals supported: `1d`, `1wk`, `1mo`

## Requirements

- Python >= 3.10
- Internet connection (data is fetched live, not stored locally)
