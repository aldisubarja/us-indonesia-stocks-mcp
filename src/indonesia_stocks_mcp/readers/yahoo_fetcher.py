"""Yahoo Finance price fetcher — get current and historical stock prices."""

from datetime import datetime, timedelta
from typing import Any

import yfinance as yf


class YahooFetcher:
    """Fetch stock prices from Yahoo Finance via yfinance."""

    def get_current_price(self, stock_code: str) -> dict:
        """Get current/latest stock price for a ticker."""
        ticker = yf.Ticker(f"{stock_code}.JK")
        info = ticker.info
        hist = ticker.history(period="1d")

        if hist.empty:
            # Try fallback: get last close
            try:
                price = info.get("previousClose") or info.get("regularMarketPrice")
            except Exception:
                price = None
        else:
            price = float(hist["Close"].iloc[-1])

        return {
            "stock_code": stock_code,
            "ticker": f"{stock_code}.JK",
            "price": round(price, 2) if price else None,
            "currency": "IDR",
            "name": info.get("longName") or info.get("shortName"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield": info.get("dividendYield"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
        }

    def get_historical(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        interval: str = "1d",
    ) -> dict:
        """Get historical OHLCV data."""
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        ticker = yf.Ticker(f"{stock_code}.JK")
        df = ticker.history(start=start_date, end=end_date, interval=interval)

        if df.empty:
            return {
                "stock_code": stock_code,
                "start_date": start_date,
                "end_date": end_date,
                "data": [],
                "message": "No data available for this period",
            }

        # Convert to list of dicts
        records = []
        for idx, row in df.iterrows():
            records.append({
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })

        return {
            "stock_code": stock_code,
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval,
            "data": records,
        }
