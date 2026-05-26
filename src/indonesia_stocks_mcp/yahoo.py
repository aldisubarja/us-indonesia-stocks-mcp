"""Yahoo Finance wrapper for Indonesian stocks (.JK suffix).

Provides: stock info, balance sheet, income statement, cash flow,
key metrics, historical prices, current price, dividend history.
"""

from __future__ import annotations

from typing import Any

import yfinance as yf


class YahooFinance:
    """Fetch Indonesian stock data from Yahoo Finance via yfinance."""

    def __init__(self) -> None:
        self._tickers: dict[str, yf.Ticker] = {}

    def _get_ticker(self, stock_code: str) -> yf.Ticker:
        """Get or create a yfinance Ticker object (cached)."""
        symbol = f"{stock_code.upper()}.JK"
        if symbol not in self._tickers:
            self._tickers[symbol] = yf.Ticker(symbol)
        return self._tickers[symbol]

    # ── Stock Info ──────────────────────────────────────────────────────

    def get_stock_info(self, stock_code: str) -> dict[str, Any]:
        """Get comprehensive stock information and valuation metrics."""
        ticker = self._get_ticker(stock_code)
        info = ticker.info

        def _get(*keys: str, default: Any = None) -> Any:
            for k in keys:
                v = info.get(k)
                if v is not None:
                    return v
            return default

        return {
            "stock_code": stock_code.upper(),
            "ticker": f"{stock_code.upper()}.JK",
            "name": _get("longName", "shortName"),
            "sector": _get("sector"),
            "industry": _get("industry"),
            "website": _get("website"),
            "description": _get("longBusinessSummary"),
            # Price
            "current_price": _get("currentPrice", "regularMarketPrice"),
            "previous_close": _get("previousClose"),
            "open": _get("open"),
            "day_high": _get("dayHigh"),
            "day_low": _get("dayLow"),
            "52_week_high": _get("fiftyTwoWeekHigh"),
            "52_week_low": _get("fiftyTwoWeekLow"),
            "beta": _get("beta"),
            # Volume & shares
            "volume": _get("volume"),
            "avg_volume": _get("averageVolume"),
            "shares_outstanding": _get("sharesOutstanding"),
            "float_shares": _get("floatShares"),
            # Valuation
            "market_cap": _get("marketCap"),
            "enterprise_value": _get("enterpriseValue"),
            "pe_ratio": _get("trailingPE"),
            "forward_pe": _get("forwardPE"),
            "peg_ratio": _get("pegRatio"),
            "price_to_book": _get("priceToBook"),
            "price_to_sales": _get("priceToSales"),
            "book_value": _get("bookValue"),
            # Dividends
            "dividend_rate": _get("dividendRate"),
            "dividend_yield": _get("dividendYield"),
            "payout_ratio": _get("payoutRatio"),
            "ex_dividend_date": _get("exDividendDate"),
            # Analyst
            "analyst_count": _get("numberOfAnalystOpinions"),
            "recommendation": _get("recommendationKey"),
            "target_mean": _get("targetMeanPrice"),
            "target_high": _get("targetHighPrice"),
            "target_low": _get("targetLowPrice"),
            # Currency
            "currency": _get("currency", "financialCurrency", default="IDR"),
        }

    # ── Financial Statements ────────────────────────────────────────────

    def get_balance_sheet(
        self, stock_code: str, period: str = "annual", all_periods: bool = True
    ) -> dict[str, Any]:
        """Get balance sheet (neraca)."""
        ticker = self._get_ticker(stock_code)
        if period == "quarterly":
            df = ticker.quarterly_balance_sheet
        else:
            df = ticker.balance_sheet
        return self._format_statement(df, stock_code, period, "balance_sheet", all_periods)

    def get_income_statement(
        self, stock_code: str, period: str = "annual", all_periods: bool = True
    ) -> dict[str, Any]:
        """Get income statement (laba rugi)."""
        ticker = self._get_ticker(stock_code)
        if period == "quarterly":
            df = ticker.quarterly_financials
        else:
            df = ticker.financials
        return self._format_statement(df, stock_code, period, "income_statement", all_periods)

    def get_cash_flow(
        self, stock_code: str, period: str = "annual", all_periods: bool = True
    ) -> dict[str, Any]:
        """Get cash flow statement (arus kas)."""
        ticker = self._get_ticker(stock_code)
        if period == "quarterly":
            df = ticker.quarterly_cashflow
        else:
            df = ticker.cashflow
        return self._format_statement(df, stock_code, period, "cash_flow", all_periods)

    def _format_statement(
        self, df, stock_code: str, period: str, statement_type: str, all_periods: bool
    ) -> dict[str, Any]:
        """Convert a pandas DataFrame to a clean dict."""
        if df is None or df.empty:
            return {
                "stock_code": stock_code.upper(),
                "statement": statement_type,
                "period": period,
                "periods": [],
                "data": [],
                "error": "No data available",
            }

        # Columns are dates (periods)
        periods = [str(c.date()) for c in df.columns]

        if not all_periods:
            periods = periods[:1]
            df = df.iloc[:, :1]

        data = []
        for i, row_name in enumerate(df.index):
            entry: dict[str, Any] = {"item": str(row_name)}
            for j, col_val in enumerate(df.iloc[i]):
                if not all_periods:
                    j = 0
                if j < len(periods):
                    try:
                        entry[periods[j]] = float(col_val) if not _is_nan(col_val) else None
                    except (TypeError, ValueError):
                        entry[periods[j]] = str(col_val) if not _is_nan(col_val) else None
                if not all_periods:
                    break
            data.append(entry)

        return {
            "stock_code": stock_code.upper(),
            "statement": statement_type,
            "period": period,
            "periods": periods,
            "data": data,
        }

    # ── Key Metrics ─────────────────────────────────────────────────────

    def get_key_metrics(self, stock_code: str) -> dict[str, Any]:
        """Get all key financial ratios and growth metrics in one call."""
        ticker = self._get_ticker(stock_code)
        info = ticker.info

        def _g(*keys: str, default: Any = None) -> Any:
            for k in keys:
                v = info.get(k)
                if v is not None:
                    return v
            return default

        return {
            "stock_code": stock_code.upper(),
            "name": _g("longName", "shortName"),
            # Profitability
            "return_on_equity": _g("returnOnEquity"),
            "return_on_assets": _g("returnOnAssets"),
            "profit_margin": _g("profitMargins"),
            "gross_margin": _g("grossMargins"),
            "operating_margin": _g("operatingMargins"),
            "ebitda_margin": _g("ebitdaMargins"),
            # Liquidity & Solvency
            "current_ratio": _g("currentRatio"),
            "quick_ratio": _g("quickRatio"),
            "debt_to_equity": _g("debtToEquity"),
            "interest_coverage": _g("interestCoverage"),
            # Growth
            "revenue_growth": _g("revenueGrowth"),
            "earnings_growth": _g("earningsGrowth"),
            # Cash Flow
            "free_cashflow": _g("freeCashflow"),
            "operating_cashflow": _g("operatingCashflow"),
            # Valuation
            "pe_ratio": _g("trailingPE"),
            "forward_pe": _g("forwardPE"),
            "peg_ratio": _g("pegRatio"),
            "price_to_book": _g("priceToBook"),
            "price_to_sales": _g("priceToSales"),
            "dividend_yield": _g("dividendYield"),
            # Per share
            "eps": _g("trailingEps"),
            "book_value_per_share": _g("bookValue"),
            # Market
            "market_cap": _g("marketCap"),
            "enterprise_value": _g("enterpriseValue"),
            "beta": _g("beta"),
            "currency": _g("currency", "financialCurrency", default="IDR"),
        }

    # ── Prices ──────────────────────────────────────────────────────────

    def get_current_price(self, stock_code: str) -> dict[str, Any]:
        """Get current/latest stock price with basic info."""
        ticker = self._get_ticker(stock_code)
        info = ticker.info
        hist = ticker.history(period="1d")

        price = None
        if not hist.empty:
            price = float(hist["Close"].iloc[-1])
        else:
            price = info.get("previousClose") or info.get("regularMarketPrice")

        return {
            "stock_code": stock_code.upper(),
            "ticker": f"{stock_code.upper()}.JK",
            "price": round(price, 2) if price else None,
            "currency": "IDR",
            "name": info.get("longName") or info.get("shortName"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield": info.get("dividendYield"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
        }

    def get_historical_prices(
        self,
        stock_code: str,
        start_date: str,
        end_date: str | None = None,
        interval: str = "1d",
    ) -> dict[str, Any]:
        """Get historical OHLCV data."""
        from datetime import datetime

        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        ticker = self._get_ticker(stock_code)
        df = ticker.history(start=start_date, end=end_date, interval=interval)

        if df.empty:
            return {
                "stock_code": stock_code.upper(),
                "start_date": start_date,
                "end_date": end_date,
                "data": [],
                "message": "No data available for this period",
            }

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
            "stock_code": stock_code.upper(),
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval,
            "data": records,
        }

    # ── Dividends ───────────────────────────────────────────────────────

    def get_dividend_history(self, stock_code: str) -> dict[str, Any]:
        """Get dividend payout history."""
        ticker = self._get_ticker(stock_code)
        div_df = ticker.dividends

        if div_df is None or div_df.empty:
            return {
                "stock_code": stock_code.upper(),
                "dividends": [],
                "message": "No dividend history available",
            }

        dividends = []
        for idx, val in div_df.items():
            dividends.append({
                "date": idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx),
                "dividend": round(float(val), 2),
                "currency": "IDR",
            })

        return {
            "stock_code": stock_code.upper(),
            "currency": "IDR",
            "dividends": dividends,
        }


def _is_nan(val: Any) -> bool:
    """Check if value is NaN (works with pandas/numpy)."""
    try:
        return bool(val != val)  # NaN != NaN
    except Exception:
        return False
