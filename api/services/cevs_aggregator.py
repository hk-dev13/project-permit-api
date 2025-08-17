from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from api.clients.global_client import KLHKClient as EPAClient
from api.clients.iso_client import ISOClient
from api.clients.eea_client import EEAClient

logger = logging.getLogger(__name__)


def _normalize_name(name: Optional[str]) -> str:
    return (name or "").strip().lower()


def compute_cevs_for_company(company_name: str, *, company_country: Optional[str] = None) -> Dict[str, Any]:
    """Compute a simple CEVS score by combining EPA, ISO, and EEA data.

    Current heuristic:
      - Base score 50
      - +30 if company has ISO 14001 certification
      - - up to 30 penalty based on EPA results count in the company's state (proxy via name contains)
      - + up to 20 boost for EEA indicator improvements (placeholder)
    """
    company_key = _normalize_name(company_name)

    # EPA: use permits data normalized list, then filter by company name
    epa_client = EPAClient()
    # Try a short-timeout EPA fetch for responsiveness
    try:
        epa_records_raw = epa_client.get_emissions_power_plants(limit=200, timeout=5.0)
    except Exception:
        epa_records_raw = epa_client.create_sample_data()
    epa_norm = epa_client.format_permit_data(epa_records_raw)
    epa_matches = epa_client.search_permits_by_company(company_name, epa_norm)

    # ISO: sample-backed; filter by country if provided, and by company name contains
    iso_client = ISOClient()
    iso_norm = iso_client.get_iso14001_certifications(country=company_country, limit=100)
    has_iso = any(_normalize_name(r.get("nama_perusahaan")) and company_key in _normalize_name(r.get("nama_perusahaan")) for r in iso_norm)

    # EEA: sample-backed; use country if provided
    eea_client = EEAClient()
    eea_norm = eea_client.get_indicator(country=company_country or None, limit=50)

    # Scoring heuristic
    score = 50.0
    components: Dict[str, Any] = {
        "base": 50.0,
        "iso_bonus": 0.0,
        "epa_penalty": 0.0,
        "eea_bonus": 0.0,
    }

    if has_iso:
        components["iso_bonus"] = 30.0
        score += 30.0

    # EPA penalty: more matches imply more emission-related footprint; cap at 30
    epa_penalty = min(30.0, float(len(epa_matches)) * 2.5)
    components["epa_penalty"] = -epa_penalty
    score -= epa_penalty

    # EEA bonus placeholder: presence of any indicator entries yields small boost
    eea_bonus = 10.0 if eea_norm else 0.0
    components["eea_bonus"] = eea_bonus
    score += eea_bonus

    # Clamp score to [0, 100]
    score = max(0.0, min(100.0, score))

    return {
        "company": company_name,
        "country": company_country,
        "score": round(score, 2),
        "components": components,
        "sources": {
            "epa_matches": len(epa_matches),
            "iso_count": len(iso_norm),
            "eea_count": len(eea_norm),
        },
        "details": {
            "epa": epa_matches,
            "iso": iso_norm,
            "eea": eea_norm,
        },
    }
