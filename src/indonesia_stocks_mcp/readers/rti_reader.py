"""RTI data reader — parse local RTI HTML files into structured JSON.

Data directory structure expected:
    STOCKS_DATA_DIR/rti/
        daftar_saham.xlsx          # stock list (columns: Kode, Nama, Saham, Papan Pencatatan, Tanggal Pencatatan)
        income_statement/{end_period}/{annual|quarter}/{code}.html
        balance_sheet/{end_period}/{annual|quarter}/{code}.html
        cash_flow/{end_period}/{annual|quarter}/{code}.html
"""

import datetime
import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
import pandas as pd


class RTIReader:
    """Parse RTI (analytics2.rti.co.id) financial statement HTML files."""

    # Row IDs for income statement
    INCOME_ROWS = {
        "total_sales": "r2c",
        "cost_of_good_sold": "r3c",
        "gross_profit": "r4c",
        "sales_and_marketing_expenses": "r5c",
        "administrative_expenses": "r6c",
        "other_operating_expenses": "r7c",
        "total_operating_expenses": "r8c",
        "operating_income": "r9c",
        "interest_income": "r10c",
        "interest_expense": "r11c",
        "foreign_exchange_gain_loss": "r12c",
        "gain_loss_on_sale_of_assets": "r13c",
        "other_items": "r14c",
        "total_other_income_expenses": "r15c",
        "income_before_tax": "r16c",
        "income_tax_expenses": "r17c",
        "income_from_normal_operations": "r18c",
        "extraordinary_items": "r19c",
        "minority_int_in_net_earnings": "r20c",
        "net_income": "r21c",
        "net_income_equity_holders": "r22c",
        "net_income_non_controlling": "r23c",
        "earning_per_share": "r25c",
        "diluted_earnings_per_share": "r26c",
        "comprehensive_income_net": "r27c",
        "other_comprehensive_income": "r28c",
        "total_comprehensive_income": "r29c",
        "comp_income_equity_holders": "r30c",
        "comp_income_non_controlling": "r31c",
    }

    # Row IDs for balance sheet
    BALANCE_ROWS = {
        "cash_and_cash_equivalents": "r2c",
        "net_receivables": "r3c",
        "inventory": "r4c",
        "prepaid_expenses": "r5c",
        "other_current_assets": "r6c",
        "total_current_assets": "r7c",
        "deferred_tax_assets": "r8c",
        "property_plant_equipment": "r9c",
        "goodwill": "r10c",
        "intangible_assets": "r11c",
        "other_assets": "r12c",
        "total_longterm_assets": "r13c",
        "total_assets": "r14c",
        "account_payables": "r15c",
        "short_term_debt": "r16c",
        "other_current_liabilities": "r17c",
        "total_current_liabilities": "r18c",
        "deferred_tax_liabilities": "r19c",
        "longterm_liabilities": "r20c",
        "total_liabilities": "r21c",
        "minority_interest": "r22c",
        "common_stock": "r23c",
        "paid_in_capital": "r24c",
        "retained_earnings": "r25c",
        "other_stockholders_equity": "r26c",
        "non_controlling_interest": "r27c",
        "total_stockholders_equity": "r28c",
        "total_liabilities_equity": "r29c",
    }

    # Row IDs for cash flow
    CASHFLOW_ROWS = {
        "cash_from_customers": "r2c",
        "payments_for_operating": "r3c",
        "other_operating_activities": "r4c",
        "cash_flow_operating": "r5c",
        "capital_expenditures": "r6c",
        "other_investing_activities": "r7c",
        "cash_flow_investing": "r8c",
        "additional_paid_in_capital": "r9c",
        "financing_related_party": "r10c",
        "dividends_paid": "r11c",
        "other_financing_activities": "r12c",
        "cash_flow_financing": "r13c",
        "net_change_in_cash": "r14c",
        "cash_beginning": "r15c",
        "exchange_rate_effect": "r16c",
        "cash_ending": "r17c",
    }

    MONTH_MAP = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "Mei": "05", "Jun": "06", "Jul": "07", "Ags": "08",
        "Sep": "09", "Okt": "10", "Nov": "11", "Des": "12",
    }

    def __init__(
        self,
        data_dir: Path,
        all: bool = True,
        ending_period: str | None = None,
        period: str = "annual",
    ):
        self.data_dir = Path(data_dir)
        self.all = all
        self.period = period
        self._ending_period = ending_period
        self._stocks_df: pd.DataFrame | None = None

    def _load_stocks(self) -> pd.DataFrame:
        if self._stocks_df is None:
            xlsx_path = self.data_dir / "daftar_saham.xlsx"
            if not xlsx_path.exists():
                raise FileNotFoundError(
                    f"daftar_saham.xlsx not found at {xlsx_path}. "
                    "Download the stock list from IDX first."
                )
            self._stocks_df = pd.read_excel(xlsx_path)
        return self._stocks_df

    def _find_ending_period(self, fin_part: str, stock_code: str) -> str:
        """Find the latest available ending period for a stock."""
        if self._ending_period:
            return self._ending_period
        part_dir = self.data_dir / fin_part
        if not part_dir.exists():
            raise FileNotFoundError(f"No {fin_part} data found at {part_dir}")
        for period_dir in sorted(part_dir.iterdir(), reverse=True):
            if not period_dir.is_dir():
                continue
            for freq_dir in sorted(period_dir.iterdir(), reverse=True):
                if not freq_dir.is_dir():
                    continue
                html_file = freq_dir / f"{stock_code}.html"
                if html_file.exists():
                    self._ending_period = period_dir.name
                    return period_dir.name
        raise FileNotFoundError(
            f"No {fin_part} data found for {stock_code} in {self.data_dir}"
        )

    def _read_html(self, fin_part: str, stock_code: str) -> str:
        ending_period = self._find_ending_period(fin_part, stock_code)
        file_path = (
            self.data_dir
            / fin_part
            / ending_period
            / self.period
            / f"{stock_code}.html"
        )
        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}. "
                f"Download RTI {fin_part} data for {stock_code} first."
            )
        return file_path.read_text(encoding="utf-8")

    def _parse_ending_periods(self, soup: BeautifulSoup) -> list[str]:
        end_num = 7 if self.period == "annual" else 6
        if not self.all:
            end_num = 2
        periods = []
        for i in range(1, end_num):
            el = soup.find(attrs={"id": f"r1c{i}"})
            if el and el.text.strip():
                periods.append(el.text.strip())
        return periods

    def _parse_years_quarters(self, periods: list[str]) -> tuple[list, list]:
        years, quarters = [], []
        for p in periods:
            if not p:
                years.append(None)
                quarters.append(None)
                continue
            parts = p.rsplit("-", 2)
            if len(parts) >= 3:
                years.append(int(parts[-1]))
                q = parts[-2]
                if q == "Mar": quarters.append(1)
                elif q == "Jun": quarters.append(2)
                elif q == "Sep": quarters.append(3)
                else: quarters.append(4)
            else:
                years.append(None)
                quarters.append(None)
        return years, quarters

    def _clean_number(self, value: str) -> float | None:
        if not value or value == "-":
            return None
        try:
            return float(value)
        except ValueError:
            pass
        # Remove ' M' suffix (millions in old format)
        value = value.replace(" M", "").replace(",", "").strip()
        try:
            return float(value)
        except ValueError:
            return None

    def _get_row_values(self, soup: BeautifulSoup, row_id: str, num_cols: int) -> list[float | None]:
        values = []
        for i in range(1, num_cols + 1):
            el = soup.find(attrs={"id": f"{row_id}{i}"})
            values.append(self._clean_number(el.text) if el and el.text.strip() else None)
        return values

    def _parse_table(
        self, soup: BeautifulSoup, row_map: dict[str, str]
    ) -> dict:
        periods = self._parse_ending_periods(soup)
        years, quarters = self._parse_years_quarters(periods)
        num_cols = len(periods)

        result = {
            "stock_code": None,
            "periods": periods,
            "years": years,
            "quarters": quarters,
        }
        for label, row_id in row_map.items():
            result[label] = self._get_row_values(soup, row_id, num_cols)
        return result

    def extract_general_info(self, stock_code: str) -> dict:
        """Extract general company info from daftar_saham.xlsx + income statement."""
        stocks = self._load_stocks()
        match = stocks[stocks["Kode"] == stock_code]
        if match.empty:
            return {"error": f"Stock {stock_code} not found in daftar_saham.xlsx"}

        row = match.iloc[0]
        # Try to get currency from income statement
        currency = "IDR"
        try:
            html = self._read_html("income_statement", stock_code)
            soup = BeautifulSoup(html, "lxml")
            curr_el = soup.find(attrs={"id": "prd"})
            if curr_el and "Rp" in curr_el.text:
                currency = "IDR"
            else:
                currency = "USD"
        except Exception:
            pass

        # Parse listed date
        date_str = row.get("Tanggal Pencatatan", "")
        listed_date = None
        if date_str and isinstance(date_str, str):
            try:
                listed_date = self._parse_listed_date(str(date_str))
            except Exception:
                listed_date = str(date_str)

        # Try to get latest price from Yahoo (optional)
        try:
            from .yahoo_fetcher import YahooFetcher
            fetcher = YahooFetcher()
            price_info = fetcher.get_current_price(stock_code)
            price = price_info.get("price")
        except Exception:
            price = None

        return {
            "stock_code": stock_code,
            "name": str(row.get("Nama", "")).strip(),
            "price": price,
            "currency": currency,
            "listed_date": listed_date,
            "shares": int(row["Saham"]) if pd.notna(row.get("Saham")) else None,
            "board": str(row.get("Papan Pencatatan", "")).strip(),
        }

    def _parse_listed_date(self, date_str: str) -> str:
        """Parse Indonesian date format like '01 Jan 2000'."""
        parts = date_str.strip().split()
        if len(parts) < 3:
            return date_str
        day = parts[0]
        month = self.MONTH_MAP.get(parts[1], parts[1])
        year = parts[2]
        return f"{year}-{month}-{day.zfill(2)}"

    def extract_income_statement(self, stock_code: str) -> dict:
        self.period = self.period  # use current setting
        html = self._read_html("income_statement", stock_code)
        soup = BeautifulSoup(html, "lxml")
        result = self._parse_table(soup, self.INCOME_ROWS)
        result["stock_code"] = stock_code
        return result

    def extract_balance_sheet(self, stock_code: str) -> dict:
        html = self._read_html("balance_sheet", stock_code)
        soup = BeautifulSoup(html, "lxml")
        result = self._parse_table(soup, self.BALANCE_ROWS)
        result["stock_code"] = stock_code
        return result

    def extract_cash_flow(self, stock_code: str) -> dict:
        html = self._read_html("cash_flow", stock_code)
        soup = BeautifulSoup(html, "lxml")
        result = self._parse_table(soup, self.CASHFLOW_ROWS)
        result["stock_code"] = stock_code
        return result

    def extract_ratios(self, stock_code: str) -> dict:
        """Extract financial ratios. Falls back to income statement for EPS."""
        html = self._read_html("income_statement", stock_code)
        soup = BeautifulSoup(html, "lxml")
        periods = self._parse_ending_periods(soup)
        years, quarters = self._parse_years_quarters(periods)
        num_cols = len(periods)

        # EPS is in row 25
        eps = self._get_row_values(soup, "r25c", num_cols)

        return {
            "stock_code": stock_code,
            "periods": periods,
            "years": years,
            "quarters": quarters,
            "eps": eps,
        }
