"""MCP server for US & Indonesian stock fundamentals via Yahoo Finance.

All data sourced from Yahoo Finance — no local data, no scrapers.
Supports IDX (.JK suffix) and US markets.
Install: uvx global-stocks-mcp
"""

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .yahoo import YahooFinance

server = Server("global-stocks-mcp")
yahoo = YahooFinance()


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


# ── Tool definitions ──────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_stock_info",
            description="Get comprehensive stock info: price, valuation (PE, PB, PEG), market cap, sector, analyst targets, beta, shares outstanding, and more. Everything you need for a summary dashboard. Use this first when analyzing a stock. Supports ID (Indonesia) and US markets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code (e.g. BBRI, BBCA, TLKM for ID; AAPL, MSFT, SPY for US)",
                    },
                    "market": {
                        "type": "string",
                        "enum": ["ID", "US"],
                        "description": "Market: ID (Indonesia, adds .JK) or US (no suffix). Default: ID.",
                    },
                },
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="get_balance_sheet",
            description="Get balance sheet (neraca): total assets, total liabilities, equity, debt, cash, investments, receivables, payables, etc. 40-50+ line items. Use period='quarterly' for quarterly data, 'annual' for annual (default). Supports ID and US markets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code (e.g. BBRI, BBCA for ID; AAPL for US)",
                    },
                    "market": {
                        "type": "string",
                        "enum": ["ID", "US"],
                        "description": "Market: ID (Indonesia, .JK) or US. Default: ID.",
                    },
                    "period": {
                        "type": "string",
                        "enum": ["annual", "quarterly"],
                        "description": "annual (default) or quarterly",
                    },
                    "all_periods": {
                        "type": "boolean",
                        "description": "True: all available periods. False: latest only. Default: True.",
                    },
                },
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="get_income_statement",
            description="Get income statement (laba rugi): revenue, gross profit, operating income, net income, EPS, EBITDA, interest, tax, etc. 30+ line items. Supports ID and US markets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code",
                    },
                    "market": {
                        "type": "string",
                        "enum": ["ID", "US"],
                        "description": "Market: ID (Indonesia, .JK) or US. Default: ID.",
                    },
                    "period": {
                        "type": "string",
                        "enum": ["annual", "quarterly"],
                        "description": "annual (default) or quarterly",
                    },
                    "all_periods": {
                        "type": "boolean",
                        "description": "True: all periods. False: latest only. Default: True.",
                    },
                },
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="get_cash_flow",
            description="Get cash flow statement (arus kas): operating, investing, financing cash flows, free cash flow, capex, dividends paid, debt issuance/repayment. 30+ line items. Supports ID and US markets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code",
                    },
                    "market": {
                        "type": "string",
                        "enum": ["ID", "US"],
                        "description": "Market: ID (Indonesia, .JK) or US. Default: ID.",
                    },
                    "period": {
                        "type": "string",
                        "enum": ["annual", "quarterly"],
                        "description": "annual (default) or quarterly",
                    },
                    "all_periods": {
                        "type": "boolean",
                        "description": "True: all periods. False: latest only. Default: True.",
                    },
                },
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="get_key_metrics",
            description="Get all key financial ratios in one call: ROE, ROA, profit margins, debt-to-equity, current ratio, revenue/earnings growth, free cashflow, PE, PB, PS, PEG, dividend yield, EPS, beta. Everything an analyst needs for a quick health check. Supports ID and US markets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code",
                    },
                    "market": {
                        "type": "string",
                        "enum": ["ID", "US"],
                        "description": "Market: ID (Indonesia, .JK) or US. Default: ID.",
                    },
                },
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="get_current_price",
            description="Get current/latest stock price with basic info (name, sector, market cap, PE, dividend yield). Lightweight — use for quick price checks or screening. Supports ID and US markets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code (e.g. BBRI, ASII, TLKM for ID; AAPL, TSLA, GOOGL for US)",
                    },
                    "market": {
                        "type": "string",
                        "enum": ["ID", "US"],
                        "description": "Market: ID (Indonesia, .JK) or US. Default: ID.",
                    },
                },
                "required": ["stock_code"],
            },
        ),
        Tool(
            name="get_historical_prices",
            description="Get historical OHLCV price data. Use for charting, technical analysis, or comparing performance over time. Supports ID and US markets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code",
                    },
                    "market": {
                        "type": "string",
                        "enum": ["ID", "US"],
                        "description": "Market: ID (Indonesia, .JK) or US. Default: ID.",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date YYYY-MM-DD",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date YYYY-MM-DD (default: today)",
                    },
                    "interval": {
                        "type": "string",
                        "enum": ["1d", "1wk", "1mo"],
                        "description": "Candle interval (default: 1d)",
                    },
                },
                "required": ["stock_code", "start_date"],
            },
        ),
        Tool(
            name="get_dividend_history",
            description="Get dividend payout history (date and amount per share). Supports ID and US markets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code",
                    },
                    "market": {
                        "type": "string",
                        "enum": ["ID", "US"],
                        "description": "Market: ID (Indonesia, .JK) or US. Default: ID.",
                    },
                },
                "required": ["stock_code"],
            },
        ),
    ]


# ── Tool handlers ─────────────────────────────────────────────────────────

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        code = arguments["stock_code"].upper()
        market = arguments.get("market", "ID")  # default ID for backward compat

        if name == "get_stock_info":
            result = yahoo.get_stock_info(code, market=market)
        elif name == "get_balance_sheet":
            result = yahoo.get_balance_sheet(
                code,
                period=arguments.get("period", "annual"),
                all_periods=arguments.get("all_periods", True),
                market=market,
            )
        elif name == "get_income_statement":
            result = yahoo.get_income_statement(
                code,
                period=arguments.get("period", "annual"),
                all_periods=arguments.get("all_periods", True),
                market=market,
            )
        elif name == "get_cash_flow":
            result = yahoo.get_cash_flow(
                code,
                period=arguments.get("period", "annual"),
                all_periods=arguments.get("all_periods", True),
                market=market,
            )
        elif name == "get_key_metrics":
            result = yahoo.get_key_metrics(code, market=market)
        elif name == "get_current_price":
            result = yahoo.get_current_price(code, market=market)
        elif name == "get_historical_prices":
            result = yahoo.get_historical_prices(
                code,
                start_date=arguments["start_date"],
                end_date=arguments.get("end_date"),
                interval=arguments.get("interval", "1d"),
                market=market,
            )
        elif name == "get_dividend_history":
            result = yahoo.get_dividend_history(code, market=market)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return [TextContent(type="text", text=_json(result))]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": type(e).__name__,
                        "message": str(e),
                    },
                    ensure_ascii=False,
                ),
            )
        ]


# ── Entry point ───────────────────────────────────────────────────────────

def main():
    """Run the MCP server via stdio."""
    import asyncio

    async def _run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(_run())
