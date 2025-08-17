from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional
import csv
import io

import requests

from api.utils.schema import ensure_iso_cert_schema

logger = logging.getLogger(__name__)


class ISOClient:
    """Client for ISO 14001 certifications (scaffold with sample fallback).

    If ISO_API_BASE is unset, returns sample data.
    """

    def __init__(self) -> None:
        self.api_base = os.getenv("ISO_API_BASE", "").rstrip("/")
        self.csv_url = os.getenv("ISO_CSV_URL", "").strip()
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "project-permit-api/1.0 (+https://github.com/hk-dev13)"
        })

    def create_sample_data(self) -> List[Dict[str, Any]]:
        return [
            {"company": "Green Energy Co", "country": "US", "certificate": "ISO 14001", "valid_until": "2026-12-31"},
            {"company": "Eco Manufacturing GmbH", "country": "DE", "certificate": "ISO 14001", "valid_until": "2025-08-01"},
            {"company": "Sustain PT", "country": "ID", "certificate": "ISO 14001", "valid_until": "2027-01-15"},
        ]

    def _load_from_csv_or_json(self, url: str) -> List[Dict[str, Any]]:
        try:
            resp = self.session.get(url, timeout=30)
            ct = (resp.headers.get("Content-Type") or "").lower()
            text = resp.text
            if "json" in ct or (text.lstrip().startswith("[") or text.lstrip().startswith("{")):
                data = resp.json()
                if isinstance(data, dict):
                    # common wrapper key
                    data = data.get("data", [])
                if not isinstance(data, list):
                    raise ValueError("Unexpected JSON shape for ISO dataset")
                return [d for d in data if isinstance(d, dict)]
            # assume CSV
            buf = io.StringIO(text)
            reader = csv.DictReader(buf)
            return [dict(row) for row in reader]
        except Exception as e:
            logger.error(f"ISO CSV/JSON load error: {e}")
            return []

    def get_iso14001_certifications(self, *, country: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        data: List[Dict[str, Any]]
        if self.csv_url:
            data = self._load_from_csv_or_json(self.csv_url)
        elif self.api_base:
            # Placeholder for future real API call
            try:
                url = f"{self.api_base}/iso1401"  # adjust when real endpoint available
                params = {"country": country} if country else {}
                resp = self.session.get(url, params=params, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    if not isinstance(data, list):
                        raise ValueError("Unexpected ISO response shape")
                else:
                    logger.warning(f"ISO API HTTP {resp.status_code}, using sample data")
                    data = self.create_sample_data()
            except Exception as e:
                logger.error(f"ISO API error: {e}")
                data = self.create_sample_data()
        else:
            data = self.create_sample_data()

        if country:
            data = [d for d in data if str(d.get("country", "")).upper() == country.upper()]
        if limit and len(data) > limit:
            data = data[:limit]
        return [ensure_iso_cert_schema(rec) for rec in data if isinstance(rec, dict)]


__all__ = ["ISOClient"]
