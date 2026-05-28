#!/usr/bin/env python3
"""Smoke test the MCP wrapper logic via direct YahooFinance calls."""
import json
from indonesia_stocks_mcp.yahoo import YahooFinance


y = YahooFinance()

def pp(title: str, obj: dict):
    print("=" * 60)
    print(title)
    print(json.dumps(obj, indent=2, ensure_ascii=False)[:800])
    print()


# ID market
pp("1. ID get_current_price BBRI", y.get_current_price("BBRI", market="ID"))
pp("2. ID get_historical_prices TLKM", y.get_historical_prices("TLKM", market="ID", start_date="2025-01-01", interval="1wk"))

# US market
pp("3. US get_current_price AAPL", y.get_current_price("AAPL", market="US"))
pp("4. US get_stock_info SPY", y.get_stock_info("SPY", market="US"))
pp("5. US get_historical_prices NVDA", y.get_historical_prices("NVDA", market="US", start_date="2025-01-01", interval="1mo"))

print("✅ SMOKE TEST DONE")
