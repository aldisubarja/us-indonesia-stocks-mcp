"""MCP server for Indonesian stock fundamentals.

Tools:
- RTI: get_income_statement, get_balance_sheet, get_cash_flow, get_ratios, get_general_info
- IDX (InlineXBRL): get_general_info, get_balance_sheet
- Yahoo Finance: get_current_price, get_historical_prices
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .readers import RTIReader, IDXReader, YahooFetcher

# ── Configuration ──────────────────────────────────────────────────────────
DATA_DIR = Path(os.environ.get("STOCKS_DATA_DIR", Path.home() / "saham"))

# ── Server ─────────────────────────────────────────────────────────────────
server = Server("indonesia-stocks-mcp")


def _json_result(data: Any) -> str:
    """Serialize to pretty JSON for MCP text response."""
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


# ── Tool definitions ──────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ── Yahoo Finance (live, no local data needed) ──
        Tool(
            name="get_current_price",
            description="Get current/latest stock price from Yahoo Finance. Stock code = ticker (e.g. BBRI, ASII, TLKM). Returns price in IDR.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code (e.g. BBRI, ASII, TLKM)"
                    }
                },
                "required": ["stock_code"]
            }
        ),
        Tool(
            name="get_historical_prices",
            description="Get historical stock prices from Yahoo Finance. Returns OHLCV data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code (e.g. BBRI, ASII, TLKM)"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date YYYY-MM-DD"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date YYYY-MM-DD (default: today)"
                    },
                    "interval": {
                        "type": "string",
                        "enum": ["1d", "1wk", "1mo"],
                        "description": "Candle interval (default: 1d)"
                    }
                },
                "required": ["stock_code", "start_date"]
            }
        ),

        # ── RTI (local HTML data) ──
        Tool(
            name="rti_get_general_info",
            description="Get general company info from RTI local data: name, listed date, shares, board, currency. Requires pre-downloaded RTI HTML files in STOCKS_DATA_DIR/rti/.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code (e.g. AALI, ASII)"
                    }
                },
                "required": ["stock_code"]
            }
        ),
        Tool(
            name="rti_get_income_statement",
            description="Get income statement (laba rugi) from RTI local data. Full P&L: sales, COGS, gross profit, operating income, net income, EPS, comprehensive income (32 fields). Requires pre-downloaded RTI HTML files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code (e.g. AALI, ASII)"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["annual", "quarter"],
                        "description": "annual or quarter (default: annual)"
                    },
                    "all_periods": {
                        "type": "boolean",
                        "description": "True: all available periods. False: latest period only (default: True)"
                    },
                    "ending_period": {
                        "type": "string",
                        "description": "Ending period date (e.g. 30-Jun-2023). Default: latest available."
                    }
                },
                "required": ["stock_code"]
            }
        ),
        Tool(
            name="rti_get_balance_sheet",
            description="Get balance sheet (neraca) from RTI local data. Assets (current/longterm), liabilities, equity (29 fields). Requires pre-downloaded RTI HTML files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["annual", "quarter"],
                        "description": "annual or quarter (default: annual)"
                    },
                    "all_periods": {
                        "type": "boolean",
                        "description": "True: all periods. False: latest only (default: True)"
                    },
                    "ending_period": {
                        "type": "string",
                        "description": "Ending period date (e.g. 30-Jun-2023)"
                    }
                },
                "required": ["stock_code"]
            }
        ),
        Tool(
            name="rti_get_cash_flow",
            description="Get cash flow (arus kas) from RTI local data. Operating, investing, financing activities (17 fields). Requires pre-downloaded RTI HTML files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["annual", "quarter"],
                        "description": "annual or quarter (default: annual)"
                    },
                    "all_periods": {
                        "type": "boolean",
                        "description": "True: all periods. False: latest only (default: True)"
                    },
                    "ending_period": {
                        "type": "string",
                        "description": "Ending period date (e.g. 30-Jun-2023)"
                    }
                },
                "required": ["stock_code"]
            }
        ),
        Tool(
            name="rti_get_ratios",
            description="Get financial ratios from RTI local data: EPS, PER, DPS, dividend yield, NPM, ROE, PBV. Requires pre-downloaded RTI HTML files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_code": {
                        "type": "string",
                        "description": "Stock ticker code"
                    }
                },
                "required": ["stock_code"]
            }
        ),

        # ── IDX InlineXBRL (local extracted HTML) ──
        Tool(
            name="idx_get_general_info",
            description="Get general company info from IDX InlineXBRL data (official IDX filings). Requires downloaded+extracted InlineXBRL HTML files in STOCKS_DATA_DIR/idx/{year}/Q{quarter}/{code}/inlineXBRL/.",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "Fiscal year (e.g. 2023)"},
                    "quarter": {"type": "integer", "description": "Quarter 1-4"},
                    "stock_code": {"type": "string", "description": "Stock ticker code (e.g. UNVR, AALI)"}
                },
                "required": ["year", "quarter", "stock_code"]
            }
        ),
        Tool(
            name="idx_get_balance_sheet",
            description="Get balance sheet (neraca) from official IDX InlineXBRL filings. Requires downloaded+extracted InlineXBRL HTML files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "Fiscal year (e.g. 2023)"},
                    "quarter": {"type": "integer", "description": "Quarter 1-4"},
                    "stock_code": {"type": "string", "description": "Stock ticker code"}
                },
                "required": ["year", "quarter", "stock_code"]
            }
        ),
        Tool(
            name="list_available_data",
            description="Scan STOCKS_DATA_DIR and list all available downloaded data: which stocks have IDX/RTI data, for which periods.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


# ── Tool handlers ─────────────────────────────────────────────────────────

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "get_current_price":
            fetcher = YahooFetcher()
            result = fetcher.get_current_price(arguments["stock_code"].upper())
            return [TextContent(type="text", text=_json_result(result))]

        elif name == "get_historical_prices":
            fetcher = YahooFetcher()
            result = fetcher.get_historical(
                stock_code=arguments["stock_code"].upper(),
                start_date=arguments["start_date"],
                end_date=arguments.get("end_date"),
                interval=arguments.get("interval", "1d"),
            )
            return [TextContent(type="text", text=_json_result(result))]

        elif name.startswith("rti_"):
            method = name.replace("rti_", "")
            params = {}
            if "period" in arguments:
                params["period"] = arguments["period"]
            if "all_periods" in arguments:
                params["all"] = arguments["all_periods"]
            if "ending_period" in arguments:
                params["ending_period"] = arguments["ending_period"]

            reader = RTIReader(data_dir=DATA_DIR / "rti", **params)
            
            if method == "get_general_info":
                result = reader.extract_general_info(arguments["stock_code"].upper())
            elif method == "get_income_statement":
                result = reader.extract_income_statement(arguments["stock_code"].upper())
            elif method == "get_balance_sheet":
                result = reader.extract_balance_sheet(arguments["stock_code"].upper())
            elif method == "get_cash_flow":
                result = reader.extract_cash_flow(arguments["stock_code"].upper())
            elif method == "get_ratios":
                result = reader.extract_ratios(arguments["stock_code"].upper())
            else:
                return [TextContent(type="text", text=f"Unknown RTI method: {method}")]
            
            return [TextContent(type="text", text=_json_result(result))]

        elif name.startswith("idx_"):
            reader = IDXReader(data_dir=DATA_DIR / "idx")
            year = arguments["year"]
            quarter = arguments["quarter"]
            code = arguments["stock_code"].upper()

            if name == "idx_get_general_info":
                result = reader.get_general_info(year, quarter, code)
            elif name == "idx_get_balance_sheet":
                result = reader.get_balance_sheet(year, quarter, code)
            else:
                return [TextContent(type="text", text=f"Unknown IDX method: {name}")]

            return [TextContent(type="text", text=_json_result(result))]

        elif name == "list_available_data":
            result = _scan_available_data(DATA_DIR)
            return [TextContent(type="text", text=_json_result(result))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except FileNotFoundError as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "DATA_NOT_FOUND", "message": str(e),
                             "hint": "Make sure you've downloaded the data. See README for data directory structure."})
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": type(e).__name__, "message": str(e)})
        )]


def _scan_available_data(data_dir: Path) -> dict:
    """Scan data directory and list what's available."""
    available = {"data_dir": str(data_dir), "idx": {}, "rti": {}}

    # Scan IDX data
    idx_dir = data_dir / "idx"
    if idx_dir.exists():
        for year_dir in sorted(idx_dir.iterdir()):
            if not year_dir.is_dir():
                continue
            year = year_dir.name
            available["idx"][year] = {}
            for q_dir in sorted(year_dir.iterdir()):
                if not q_dir.is_dir() or not q_dir.name.startswith("Q"):
                    continue
                quarter = q_dir.name
                stocks = [
                    s.name for s in sorted(q_dir.iterdir())
                    if s.is_dir() and (s / "inlineXBRL").exists()
                ]
                if stocks:
                    available["idx"][year][quarter] = stocks

    # Scan RTI data
    rti_dir = data_dir / "rti"
    if rti_dir.exists():
        available["rti"]["has_daftar_saham"] = (rti_dir / "daftar_saham.xlsx").exists()
        for fin_part in ["income_statement", "balance_sheet", "cash_flow"]:
            part_dir = rti_dir / fin_part
            if part_dir.exists():
                available["rti"][fin_part] = {}
                for period_dir in sorted(part_dir.iterdir()):
                    if not period_dir.is_dir():
                        continue
                    available["rti"][fin_part][period_dir.name] = {}
                    for freq_dir in sorted(period_dir.iterdir()):
                        if not freq_dir.is_dir():
                            continue
                        stocks = [f.stem for f in sorted(freq_dir.glob("*.html"))]
                        if stocks:
                            available["rti"][fin_part][period_dir.name][freq_dir.name] = stocks

    return available


# ── Entry point ───────────────────────────────────────────────────────────

def main():
    """Run the MCP server via stdio."""
    import asyncio
    asyncio.run(_run())


async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
