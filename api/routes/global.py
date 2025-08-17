from __future__ import annotations

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from api.clients.global_client import KLHKClient
from api.utils import cache as cache_util


global_bp = Blueprint("global_bp", __name__)

logger = logging.getLogger(__name__)


def _fetch_and_normalize() -> List[Dict[str, Any]]:
    """Fetch fresh EPA emissions data and normalize to our schema."""
    logger.info("Fetching fresh EPA emissions data (global route)")
    client = KLHKClient()
    try:
        raw = client.get_status_sk(plain=False)
        data = raw if (raw and isinstance(raw, list)) else client.create_sample_data()
    except Exception as e:
        logger.error(f"Error fetching EPA data: {e}")
        data = client.create_sample_data()

    normalized = client.format_permit_data(data)
    return normalized


def _get_cached_data() -> List[Dict[str, Any]]:
    data = cache_util.get_or_set(_fetch_and_normalize)
    ts = cache_util.get_cache_timestamp()
    if ts:
        try:
            current_app.config["CACHE_TIMESTAMP"] = ts
        except Exception:
            pass
    return data


def _matches_filters(item: Dict[str, Any], *, state: Optional[str], year: Optional[int], pollutant: Optional[str]) -> bool:
    if state:
        # Prefer normalized extras.state, then raw.state/state_name
        extras = item.get("extras") or {}
        raw = extras.get("raw", {})
        st = str(extras.get("state") or raw.get("state") or raw.get("state_name") or "")
        if st.lower() != state.lower():
            return False

    if year is not None:
        # Our normalized year is in tanggal_berlaku as str
        y = item.get("tanggal_berlaku")
        if str(y) != str(year):
            return False

    if pollutant:
        pol = str(item.get("judul_kegiatan") or "")
        if pollutant.lower() not in pol.lower():
            return False

    return True


@global_bp.route("/global/emissions", methods=["GET"])
def global_emissions():
    """EPA power plant emissions with optional filters and pagination.

    Query params:
      - state: 2-letter state code (e.g., TX)
      - year: integer year
      - pollutant: e.g., CO2
      - page: default 1
      - limit: default 50 (1..100)
    """
    try:
        state = request.args.get("state")
        year_str = request.args.get("year")
        pollutant = request.args.get("pollutant")
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 50))

        year = int(year_str) if year_str and year_str.isdigit() else None
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 50

        data = _get_cached_data()

        # Apply filters in-memory (we cache the full normalized list)
        filtered = [d for d in data if _matches_filters(d, state=state, year=year, pollutant=pollutant)]

        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated = filtered[start_idx:end_idx]

        return jsonify({
            "status": "success",
            "data": paginated,
            "filters": {"state": state, "year": year, "pollutant": pollutant},
            "pagination": {
                "page": page,
                "limit": limit,
                "total_records": len(filtered),
                "total_pages": (len(filtered) + limit - 1) // limit,
                "has_next": end_idx < len(filtered),
                "has_prev": page > 1,
            },
            "retrieved_at": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Error in /global/emissions: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@global_bp.route("/global/emissions/stats", methods=["GET"])
def global_emissions_stats():
    """Basic stats aggregated by state, pollutant, and year."""
    try:
        data = _get_cached_data()

        by_state: Dict[str, int] = {}
        by_pollutant: Dict[str, int] = {}
        by_year: Dict[str, int] = {}

        for item in data:
            raw = (item.get("extras") or {}).get("raw", {})
            state = str(raw.get("state") or raw.get("state_name") or "Unknown") or "Unknown"
            pol = str(item.get("judul_kegiatan") or "Unknown") or "Unknown"
            year = str(item.get("tanggal_berlaku") or "Unknown") or "Unknown"

            by_state[state] = by_state.get(state, 0) + 1
            by_pollutant[pol] = by_pollutant.get(pol, 0) + 1
            by_year[year] = by_year.get(year, 0) + 1

        return jsonify({
            "status": "success",
            "statistics": {
                "by_state": by_state,
                "by_pollutant": by_pollutant,
                "by_year": by_year,
                "total_records": len(data),
            },
            "retrieved_at": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Error in /global/emissions/stats: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
