from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional
import csv
import io

import requests

from api.utils.schema import ensure_eea_env_schema

logger = logging.getLogger(__name__)


class EEAClient:
    """Client for EEA environmental datasets (scaffold).

    If EEA_API_BASE is unset, returns sample data.
    """

    def __init__(self) -> None:
        self.api_base = os.getenv("EEA_API_BASE", "").rstrip("/")
        self.csv_url = os.getenv("EEA_CSV_URL", "").strip()
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "project-permit-api/1.0 (+https://github.com/hk-dev13)"
        })

    def create_sample_data(self) -> List[Dict[str, Any]]:
        return [
            {"country": "SE", "indicator": "GHG", "year": 2023, "value": 123.4, "unit": "MtCO2e"},
            {"country": "DE", "indicator": "GHG", "year": 2023, "value": 456.7, "unit": "MtCO2e"},
            {"country": "PL", "indicator": "GHG", "year": 2023, "value": 210.2, "unit": "MtCO2e"},
        ]

    def _load_from_csv_or_json(self, url: str) -> List[Dict[str, Any]]:
        try:
            resp = self.session.get(url, timeout=30)
            ct = (resp.headers.get("Content-Type") or "").lower()
            text = resp.text
            if "json" in ct or (text.lstrip().startswith("[") or text.lstrip().startswith("{")):
                data = resp.json()
                if isinstance(data, dict):
                    data = data.get("data", [])
                if not isinstance(data, list):
                    raise ValueError("Unexpected JSON shape for EEA dataset")
                return [d for d in data if isinstance(d, dict)]
            buf = io.StringIO(text)
            reader = csv.DictReader(buf)
            return [dict(row) for row in reader]
        except Exception as e:
            logger.error(f"EEA CSV/JSON load error: {e}")
            return []

    def get_indicator(self, *, indicator: str = "GHG", country: Optional[str] = None, year: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        if self.csv_url:
            data = self._load_from_csv_or_json(self.csv_url)
        elif self.api_base:
            try:
                url = f"{self.api_base}/indicator/{indicator}"  # placeholder
                params: Dict[str, Any] = {}
                if country:
                    params["country"] = country
                if year is not None:
                    params["year"] = year
                resp = self.session.get(url, params=params, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if not isinstance(data, list):
                        raise ValueError("Unexpected EEA response shape")
                else:
                    logger.warning(f"EEA API HTTP {resp.status_code}, using sample data")
                    data = self.create_sample_data()
            except Exception as e:
                logger.error(f"EEA API error: {e}")
                data = self.create_sample_data()
        else:
            data = self.create_sample_data()

        if country:
            data = [d for d in data if str(d.get("country", "")).upper() == country.upper()]
        if year is not None:
            data = [d for d in data if int(d.get("year") or 0) == int(year)]
        if limit and len(data) > limit:
            data = data[:limit]
        return [ensure_eea_env_schema(rec) for rec in data if isinstance(rec, dict)]


__all__ = ["EEAClient"]
