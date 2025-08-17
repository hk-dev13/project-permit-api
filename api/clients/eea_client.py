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
            # Excel support
            if url.lower().endswith(".xlsx") or "spreadsheetml" in ct:
                try:
                    try:
                        import pandas as pd  # type: ignore
                    except Exception as ie:
                        logger.warning(f"pandas not available for XLSX parsing: {ie}")
                        return []
                    df = pd.read_excel(io.BytesIO(resp.content))
                    return df.to_dict(orient="records")  # type: ignore[return-value]
                except Exception as e:
                    logger.error(f"EEA XLSX parse error: {e}")
                    return []
            text = resp.text
            if "json" in ct or (text.lstrip().startswith("[") or text.lstrip().startswith("{")):
                data = resp.json()
                if isinstance(data, dict):
                    # Accept common container keys
                    for key in ("data", "items", "results", "records"):
                        if key in data and isinstance(data[key], list):
                            data = data[key]
                            break
                    else:
                        data = []
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

    def get_countries_renewables(self, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load country renewables share dataset and normalize keys.

        Prefers env EEA_RENEWABLES_SOURCE, then EEA_CSV_URL, then local file in repo.
        """
        src = (source or os.getenv("EEA_RENEWABLES_SOURCE") or os.getenv("EEA_CSV_URL")
               or os.path.join(os.getcwd(), "countries-breakdown-actual-res-progress-13.csv"))
        data = self._load_csv_any(src)
        out: List[Dict[str, Any]] = []
        for r in data:
            # Headers may contain type suffix after ':'
            def g(key: str) -> Optional[str]:
                if key in r:
                    return r.get(key)
                # try without type suffix
                for k in r.keys():
                    if k.split(":")[0].strip().lower() == key.lower():
                        return r.get(k)
                return None

            country = (g("Country") or "").strip()
            if not country:
                continue
            val20 = g("Renewable energy share 2020")
            val21 = g("Renewable energy share 2021")
            target20 = g("2020 Target")
            try:
                ren20 = float(val20) if (val20 is not None and str(val20).strip() != "") else None
            except Exception:
                ren20 = None
            try:
                ren21 = float(val21) if (val21 is not None and str(val21).strip() != "") else None
            except Exception:
                ren21 = None
            try:
                tgt20 = float(target20) if (target20 is not None and str(target20).strip() != "") else None
            except Exception:
                tgt20 = None
            out.append({
                "country": country,
                "renewable_energy_share_2020": ren20,
                # as requested: use 2021 column as proxy
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

    def get_industrial_pollution(self, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load industrial pollutants time series (index=2010=100 style).

        Prefers env EEA_POLLUTION_SOURCE, then local repo CSV.
        """
        src = (source or os.getenv("EEA_POLLUTION_SOURCE")
               or os.path.join(os.getcwd(), "industrial-releases-of-pollutants-to.csv"))
        data = self._load_csv_any(src)
        # Normalize
        norm: List[Dict[str, Any]] = []
        for r in data:
            def g(key: str) -> Optional[str]:
                if key in r:
                    return r.get(key)
                for k in r.keys():
                    if k.split(":")[0].strip().lower() == key.lower():
                        return r.get(k)
                return None
            y = g("Year")
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
                "cd_hg_ni_pb": to_float(g("Cd, Hg, Ni, Pb")),
                "toc": to_float(g("TOC")),
                "total_n": to_float(g("Total N")),
                "total_p": to_float(g("Total P")),
                "gva": to_float(g("GVA")),
            })
        # sort by year
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
