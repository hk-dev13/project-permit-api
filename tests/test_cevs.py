from __future__ import annotations

import os

from api.services.cevs_aggregator import compute_cevs_for_company


def test_cevs_basic_runs_without_country():
    res = compute_cevs_for_company("Test Company")
    assert isinstance(res, dict)
    assert "score" in res and isinstance(res["score"], float)
    assert "components" in res


def test_cevs_with_country_uses_sources_field():
    res = compute_cevs_for_company("Test Company", company_country="Sweden")
    sources = res.get("sources", {})
    assert "edgar_source" in sources
    assert "renewables_source" in sources
    assert "pollution_trend_source" in sources


def test_env_switch_pollution_source_edgar(monkeypatch):
    # Force EDGAR selection; data presence may vary but field should reflect selection
    monkeypatch.setenv("CEVS_POLLUTION_SOURCE", "edgar")
    res = compute_cevs_for_company("Test Company", company_country="United States")
    assert res["sources"].get("pollution_trend_source") == "edgar"


def test_env_switch_pollution_source_auto(monkeypatch):
    monkeypatch.setenv("CEVS_POLLUTION_SOURCE", "auto")
    res = compute_cevs_for_company("Test Company", company_country="Austria")
    assert res["sources"].get("pollution_trend_source") in ("auto", "eea", "edgar")
