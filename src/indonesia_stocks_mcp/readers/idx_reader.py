"""IDX InlineXBRL reader — parse official IDX financial statement HTML files.

Data directory structure expected:
    STOCKS_DATA_DIR/idx/{year}/Q{quarter}/{code}/inlineXBRL/*.html
    - File 0: general info
    - File 1: balance sheet (neraca)
    - File 2: income statement (laba rugi) — partially implemented upstream
"""

import json
import os
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


class IDXReader:
    """Parse IDX InlineXBRL extracted HTML files."""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)

    def _get_xbrl_dir(self, year: int, quarter: int, stock_code: str) -> Path:
        d = self.data_dir / str(year) / f"Q{quarter}" / stock_code / "inlineXBRL"
        if not d.exists():
            raise FileNotFoundError(
                f"IDX data not found: {d}. "
                f"Download InlineXBRL for {stock_code} {year} Q{quarter} first."
            )
        return d

    def _read_file(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")

    def _get_xbrl_files(self, xbrl_dir: Path) -> list[Path]:
        files = sorted([f for f in xbrl_dir.iterdir() if f.suffix == ".html"])
        if not files:
            raise FileNotFoundError(f"No HTML files found in {xbrl_dir}")
        return files

    def _parse_general_info_columns(self, soup: BeautifulSoup) -> list[str]:
        cols = soup.find_all(attrs={"class": "rowHeaderEN01"})
        return [col.text.replace(" ", "_").lower() for col in cols]

    def _parse_general_info_values(self, soup: BeautifulSoup) -> list[str]:
        cols = soup.find_all(attrs={"class": "valueCell"})
        return [re.sub(r"\s+", " ", col.text.replace("\n", "").strip()) for col in cols]

    def get_general_info(self, year: int, quarter: int, stock_code: str) -> dict:
        """Parse general company info from InlineXBRL file 0."""
        xbrl_dir = self._get_xbrl_dir(year, quarter, stock_code)
        files = self._get_xbrl_files(xbrl_dir)
        soup = BeautifulSoup(self._read_file(files[0]), "lxml")
        keys = self._parse_general_info_columns(soup)
        vals = self._parse_general_info_values(soup)
        info = dict(zip(keys, vals))
        info["stock_code"] = stock_code
        info["year"] = year
        info["quarter"] = quarter
        return info

    def get_balance_sheet(self, year: int, quarter: int, stock_code: str) -> dict:
        """Parse balance sheet (neraca) from InlineXBRL file 1."""
        xbrl_dir = self._get_xbrl_dir(year, quarter, stock_code)
        files = self._get_xbrl_files(xbrl_dir)
        if len(files) < 2:
            raise FileNotFoundError(
                f"Balance sheet file not found. Need at least 2 files in {xbrl_dir}"
            )

        soup = BeautifulSoup(self._read_file(files[1]), "lxml")
        trows = soup.find_all("tr", {"style": ""})

        columns = []
        values = []

        for row in trows:
            cols = row.find_all("td", {"class": "rowHeaderEN01"})
            for col in cols:
                columns.append(col.contents[0].replace(" ", "_").lower())
            vals = row.find_all("ix:nonfraction", {"contextref": "CurrentYearInstant"})
            if vals:
                numb_str = re.sub(r"\s+", "", vals[0].contents[0].replace("\n", ""))
                try:
                    values.append(float(numb_str.replace(",", "")))
                except (ValueError, IndexError):
                    values.append(None)
            else:
                values.append(None)

        # Build dict matching columns to values (skip first 2 header values)
        result = {
            "stock_code": stock_code,
            "year": year,
            "quarter": quarter,
        }
        for k, v in zip(columns, values[2:]):
            result[k] = v

        return result
