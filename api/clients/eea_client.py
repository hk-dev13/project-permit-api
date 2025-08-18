from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional

import io
import csv
import requests
import pandas as pd
from api.utils.schema import ensure_eea_env_schema

logger = logging.getLogger(__name__)



class EEAClient:
    """Client for EEA environmental datasets (Parquet API).

    Uses the new EEA API (https://eeadmz1-downloads-api-appservice.azurewebsites.net) to fetch Parquet files.
    """

    BASE_URL = "https://eeadmz1-downloads-api-appservice.azurewebsites.net"

    # These dataset IDs should be updated if EEA changes them
    DATASET_IDS = {
        "renewables": "share-of-energy-from-renewable-sources",  # Example, update as needed
        "industrial_pollution": "industrial-releases-of-pollutants-to-water",  # Example, update as needed
    }

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/octet-stream",
            "User-Agent": "project-permit-api/1.0 (+https://github.com/hk-dev13)"
        })

    def create_sample_data(self) -> List[Dict[str, Any]]:
        return [
            {"country": "SE", "indicator": "GHG", "year": 2023, "value": 123.4, "unit": "MtCO2e"},
            {"country": "DE", "indicator": "GHG", "year": 2023, "value": 456.7, "unit": "MtCO2e"},
            {"country": "PL", "indicator": "GHG", "year": 2023, "value": 210.2, "unit": "MtCO2e"},
        ]


    def _download_parquet(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Download and parse a Parquet file from the EEA API."""
        url = f"{self.BASE_URL}/api/Download/{dataset_id}"
        try:
            resp = self.session.get(url, timeout=60)
            resp.raise_for_status()
            df = pd.read_parquet(io.BytesIO(resp.content))
            return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"EEA Parquet download/parse error for {dataset_id}: {e}")
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

    # --- New: local/remote CSV helpers for renewables and industrial pollution ---
    def _read_local_csv(self, path: str) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # skip empty rows
                    if not any(v and str(v).strip() for v in row.values()):
                        continue
                    rows.append(dict(row))
        except Exception as e:
            logger.error(f"EEA local CSV read error ({path}): {e}")
        return rows

    def _load_csv_any(self, source: str) -> List[Dict[str, Any]]:
        if source.lower().startswith(("http://", "https://")):
            return self._load_from_csv_or_json(source)
        # treat as local path
        return self._read_local_csv(source)


    def get_countries_renewables(self) -> List[Dict[str, Any]]:
        """Load country renewables share dataset from EEA Parquet API."""
        data = self._download_parquet(self.DATASET_IDS["renewables"])
        out: List[Dict[str, Any]] = []
        for r in data:
            # Adjust these keys as needed to match the Parquet schema
            country = (r.get("Country") or r.get("country") or "").strip()
            if not country:
                continue
            ren20 = r.get("Renewable energy share 2020") or r.get("renewable_energy_share_2020")
            ren21 = r.get("Renewable energy share 2021") or r.get("renewable_energy_share_2021")
            tgt20 = r.get("2020 Target") or r.get("target_2020")
            try:
                ren20 = float(ren20) if ren20 is not None and str(ren20).strip() != "" else None
            except Exception:
                ren20 = None
            try:
                ren21 = float(ren21) if ren21 is not None and str(ren21).strip() != "" else None
            except Exception:
                ren21 = None
            try:
                tgt20 = float(tgt20) if tgt20 is not None and str(tgt20).strip() != "" else None
            except Exception:
                tgt20 = None
            out.append({
                "country": country,
                "renewable_energy_share_2020": ren20,
                "renewable_energy_share_2021_proxy": ren21,
                "target_2020": tgt20,
            })
        return out

    def get_country_renewables(self, country: Optional[str], source: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not country:
            return None
        country_l = country.strip().lower()
        for r in self.get_countries_renewables(source=source):
            if r.get("country", "").strip().lower() == country_l:
                return r
        return None


    def get_industrial_pollution(self) -> List[Dict[str, Any]]:
        """Load industrial pollutants time series from EEA Parquet API."""
        data = self._download_parquet(self.DATASET_IDS["industrial_pollution"])
        norm: List[Dict[str, Any]] = []
        for r in data:
            # Adjust keys as needed to match the Parquet schema
            y = r.get("Year") or r.get("year")
            try:
                year = int(float(y)) if y not in (None, "") else None
            except Exception:
                year = None
            if not year:
                continue
            def to_float(v):
                try:
                    return float(v) if v not in (None, "") else None
                except Exception:
                    return None
            norm.append({
                "year": year,
                "cd_hg_ni_pb": to_float(r.get("Cd, Hg, Ni, Pb") or r.get("cd_hg_ni_pb")),
                "toc": to_float(r.get("TOC") or r.get("toc")),
                "total_n": to_float(r.get("Total N") or r.get("total_n")),
                "total_p": to_float(r.get("Total P") or r.get("total_p")),
                "gva": to_float(r.get("GVA") or r.get("gva")),
            })
        norm.sort(key=lambda x: x.get("year", 0))
        return norm

    def compute_pollution_trend(self, records: List[Dict[str, Any]], window: int = 3) -> Dict[str, Any]:
        """Compute simple trend over the last `window` records for total_n and total_p.

        Returns {'total_n': {'slope': float, 'increase': bool}, 'total_p': {...}}
        """
        def slope_for(key: str) -> Dict[str, Any]:
            vals = [r.get(key) for r in records if isinstance(r.get(key), (int, float))]
            if len(vals) < 2:
                return {"slope": 0.0, "increase": False}
            sel = vals[-window:] if len(vals) >= window else vals
            s = float(sel[-1] - sel[0])
            return {"slope": s, "increase": s > 0.0}
        tn = slope_for("total_n")
        tp = slope_for("total_p")
        return {"total_n": tn, "total_p": tp}


__all__ = ["EEAClient"]
