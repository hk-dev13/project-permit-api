from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import os

from api.clients.global_client import KLHKClient as EPAClient
from api.clients.iso_client import ISOClient
from api.clients.eea_client import EEAClient
from api.clients.edgar_client import EDGARClient
from api.utils.policy import load_best_practices, practices_for_country

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

    # EEA: use indicator sample plus new CSV-based datasets (renewables and industrial pollution)
    eea_client = EEAClient()
    eea_norm = eea_client.get_indicator(country=company_country or None, limit=50)
    # New: country renewables row and EU average row for comparison
    renew_row = eea_client.get_country_renewables(company_country) if company_country else None
    renew_all = eea_client.get_countries_renewables()
    eu_row = next((r for r in renew_all if (r.get("country") or "").strip().lower() in ("eu-27", "eu27", "eu 27", "eu")), None)
    # New: industrial pollution timeseries/trend from EEA (global, not per company)
    pol_series = eea_client.get_industrial_pollution()
    pol_trend = eea_client.compute_pollution_trend(pol_series) if pol_series else {"total_n": {"increase": False}, "total_p": {"increase": False}}
    # New: EDGAR country trends as fallback/augmentation if country provided
    edgar_details: Dict[str, Any] = {}
    if company_country:
        try:
            edgar_client = EDGARClient()
            # Prefer PM2.5 and NOx as air-quality related proxies
            pm_tr = edgar_client.compute_country_trend(company_country, pollutant="PM2.5")
            nox_tr = edgar_client.compute_country_trend(company_country, pollutant="NOx")
            edgar_details = {"pm25": pm_tr, "nox": nox_tr}
        except Exception as e:
            logger.warning(f"EDGAR trend load failed: {e}")

    # Scoring heuristic
    score = 50.0
    components: Dict[str, Any] = {
        "base": 50.0,
        "iso_bonus": 0.0,
        "epa_penalty": 0.0,
        "eea_bonus": 0.0,
        "renewables_bonus": 0.0,
        "pollution_penalty": 0.0,
    "policy_bonus": 0.0,
    }

    if has_iso:
        components["iso_bonus"] = 30.0
        score += 30.0

    # EPA penalty: more matches imply more emission-related footprint; cap at 30
    epa_penalty = min(30.0, float(len(epa_matches)) * 2.5)
    components["epa_penalty"] = -epa_penalty
    score -= epa_penalty

    # EEA bonus placeholder: presence of any indicator entries yields small boost
    eea_bonus = 5.0 if eea_norm else 0.0
    components["eea_bonus"] = eea_bonus
    score += eea_bonus

    # Renewables bonus (dynamic): reward exceeding target and EU average
    renew_bonus = 0.0
    renew_details: Dict[str, Any] = {}
    if renew_row and isinstance(renew_row.get("renewable_energy_share_2021_proxy"), (int, float)):
        share = float(renew_row["renewable_energy_share_2021_proxy"])  # %
        target = float(renew_row.get("target_2020") or 0.0)
        eu_share = None
        if eu_row and isinstance(eu_row.get("renewable_energy_share_2021_proxy"), (int, float)):
            eu_share = float(eu_row["renewable_energy_share_2021_proxy"])  # % EU-27 2021

        # Weights: how much to reward beating target vs EU average
        W_TARGET = 0.5  # pts per 1% over target
        W_EU = 0.2      # pts per 1% over EU average
        MAX_RENEW = 20.0

        bonus_target = max(0.0, (share - target)) * W_TARGET
        bonus_eu = max(0.0, (share - (eu_share or 0.0))) * W_EU
        renew_bonus = min(MAX_RENEW, bonus_target + bonus_eu)

        renew_details = {
            "share_2021": round(share, 2),
            "target_2020": round(target, 2) if target else None,
            "eu_share_2021": round(eu_share, 2) if eu_share is not None else None,
            "bonus_from_target": round(bonus_target, 2),
            "bonus_from_eu": round(bonus_eu, 2),
            "weights": {"W_TARGET": W_TARGET, "W_EU": W_EU},
            "cap": MAX_RENEW,
        }

    components["renewables_bonus"] = round(renew_bonus, 2)
    score += renew_bonus

    # Industrial pollution penalty with source selection (ENV: CEVS_POLLUTION_SOURCE=auto|eea|edgar)
    pol_penalty = 0.0
    pol_details: Dict[str, Any] = {}
    source_pref = (os.getenv("CEVS_POLLUTION_SOURCE") or "auto").strip().lower()
    chosen_source = "eea"
    if source_pref == "edgar" and edgar_details:
        chosen_source = "edgar"
    elif source_pref == "auto":
        chosen_source = "eea" if pol_series else ("edgar" if edgar_details else "eea")
    else:
        chosen_source = "eea"

    if chosen_source == "eea" and isinstance(pol_trend, dict):
        def slope_for(key: str) -> Dict[str, Any]:
            vals = [r.get(key) for r in pol_series if isinstance(r.get(key), (int, float))]
            if len(vals) < 2:
                return {"slope": 0.0, "increase": False}
            sel = vals[-3:] if len(vals) >= 3 else vals
            s = float(sel[-1] - sel[0])
            return {"slope": s, "increase": s > 0.0}

        keys_weights = {"cd_hg_ni_pb": 6.0, "total_n": 4.0, "total_p": 4.0, "toc": 3.0}
        trend_all: Dict[str, Any] = {}
        for k, w in keys_weights.items():
            tr = slope_for(k)
            trend_all[k] = tr
            if tr.get("increase"):
                slope = float(tr.get("slope") or 0.0)
                intensity = min(max(slope / 10.0, 0.0), 1.0)
                pol_penalty += w * intensity
        pol_details = {"source": "eea", "trends": trend_all, "weights": keys_weights, "scaled_penalty": round(pol_penalty, 2)}
        if edgar_details:
            pol_details["edgar"] = edgar_details
    elif chosen_source == "edgar" and edgar_details and company_country:
        weights = {"PM2.5": 8.0, "NOx": 7.0}
        trends: Dict[str, Any] = {}
        try:
            edgar_client = EDGARClient()
            for pol, w in [("PM2.5", weights["PM2.5"]), ("NOx", weights["NOx"])]:
                tr = edgar_client.get_country_emissions_trend(company_country, pollutant=pol)
                series = edgar_client.get_country_series(company_country, pol)
                end_val = float(series[-1]["value"]) if series else 0.0
                delta = float(tr.get("slope") or 0.0)
                rel = (delta / max(abs(end_val), 1.0)) if tr.get("increase") else 0.0
                intensity = min(max(rel, 0.0), 1.0)
                pol_penalty += w * intensity
                trends[pol] = {"trend": tr, "end_value": end_val, "intensity": round(intensity, 4)}
            pol_details = {"source": "edgar", "trends": trends, "weights": weights, "scaled_penalty": round(pol_penalty, 2)}
        except Exception as e:
            logger.warning(f"EDGAR penalty computation failed: {e}")

    pol_penalty = min(15.0, pol_penalty)
    components["pollution_penalty"] = -pol_penalty
    score -= pol_penalty

    # Policy incentives bonus: if country has practices referencing ISO 14001 and company has ISO
    policy_bonus = 0.0
    policy_details: Dict[str, Any] = {}
    if has_iso and company_country:
        practices = load_best_practices()
        country_pracs = practices_for_country(practices, company_country)
        # Look for impactful typologies
        impactful = {"Fast-track permits/simplification in the application", "Reduced inspection frequencies", "Reduced reporting and monitoring requirements"}
        matches = [p for p in country_pracs if (p.get("scheme") and "iso 14001" in p.get("scheme", "").lower()) and (p.get("typology") in impactful)]
        # +1 per impactful practice up to +3
        policy_bonus = float(min(3, len(matches)))
        policy_details = {"practices": matches[:5], "count": len(matches)}
    components["policy_bonus"] = policy_bonus
    score += policy_bonus

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
            "renewables_source": os.getenv("EEA_RENEWABLES_SOURCE") or os.getenv("EEA_CSV_URL") or "local:countries-breakdown-actual-res-progress-13.csv",
            "pollution_source": os.getenv("EEA_POLLUTION_SOURCE") or "local:industrial-releases-of-pollutants-to.csv",
            "edgar_source": os.getenv("EDGAR_XLSX_PATH") or "local:EDGAR_emiss_on_UCDB_2024.xlsx",
            "policy_source": os.getenv("POLICY_XLSX_PATH") or "local:Annex III_Best practices and justifications.xlsx",
            "pollution_trend_source": os.getenv("CEVS_POLLUTION_SOURCE") or "auto",
        },
        "details": {
            "epa": epa_matches,
            "iso": iso_norm,
            "eea": eea_norm,
            "renewables": {"country_row": renew_row, "eu_row": eu_row, "bonus_calc": renew_details},
            "pollution_trend": pol_details or pol_trend,
            "policy": policy_details,
        },
    }
