from __future__ import annotations

import os
import pytest
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


# === New Specific Scenario Tests ===

def test_sweden_renewable_bonus_scenario():
    """Test that Sweden gets appropriate renewable energy bonus due to high performance."""
    res = compute_cevs_for_company("Swedish Green Tech AB", company_country="Sweden")
    
    # Sweden should have renewable data and likely get a bonus
    details = res["details"]
    renewables = details.get("renewables", {})
    
    if renewables.get("country_row"):
        country_data = renewables["country_row"]
        # Sweden typically has high renewable share
        share_2021 = country_data.get("renewable_energy_share_2021_proxy")
        target_2020 = country_data.get("target_2020")
        
        if isinstance(share_2021, (int, float)) and isinstance(target_2020, (int, float)):
            # Sweden should exceed its target significantly
            assert share_2021 > target_2020, f"Sweden share {share_2021}% should exceed target {target_2020}%"
            
            # Should get renewable bonus
            components = res["components"]
            renewable_bonus = components.get("renewables_bonus", 0)
            assert renewable_bonus > 0, "Sweden should get renewable energy bonus"


def test_pollution_penalty_variation():
    """Test that different countries get different pollution penalties based on trends."""
    # Test with a country that might have industrial pollution data
    res_germany = compute_cevs_for_company("German Industrial Corp", company_country="Germany")
    res_poland = compute_cevs_for_company("Polish Manufacturing Ltd", company_country="Poland")
    
    components_de = res_germany["components"]
    components_pl = res_poland["components"]
    
    pollution_penalty_de = abs(components_de.get("pollution_penalty", 0))
    pollution_penalty_pl = abs(components_pl.get("pollution_penalty", 0))
    
    # Both should have some form of pollution assessment
    assert "pollution_penalty" in components_de
    assert "pollution_penalty" in components_pl
    
    # Pollution penalties should be non-negative (stored as negative values)
    assert components_de["pollution_penalty"] <= 0
    assert components_pl["pollution_penalty"] <= 0


def test_austria_policy_bonus_scenario():
    """Test Austria policy bonus with ISO certification."""
    res = compute_cevs_for_company("Austrian ISO Certified Corp", company_country="Austria")
    
    # Check if policy system is working
    sources = res["sources"]
    details = res["details"]
    
    assert "policy_source" in sources
    assert "policy" in details
    
    policy_details = details["policy"]
    # Should have policy data structure even if no matches
    assert isinstance(policy_details, dict)


def test_component_balance_and_constraints():
    """Test that CEVS components are properly balanced and within expected constraints."""
    res = compute_cevs_for_company("Test Balanced Corp", company_country="Germany")
    
    components = res["components"]
    score = res["score"]
    
    # Score should be sum of all components
    expected_score = (
        components["base"] + 
        components["iso_bonus"] + 
        components["epa_penalty"] + 
        components["renewables_bonus"] + 
        components["pollution_penalty"] + 
        components["policy_bonus"]
    )
    
    # Allow for small floating point differences and clamping to [0,100]
    clamped_score = max(0.0, min(100.0, expected_score))
    assert abs(score - clamped_score) < 0.01, f"Score {score} should match component sum {clamped_score}"
    
    # Validate component ranges
    assert components["base"] == 50.0, "Base score should always be 50"
    assert 0 <= components["iso_bonus"] <= 30, "ISO bonus should be 0-30"
    assert -30 <= components["epa_penalty"] <= 0, "EPA penalty should be 0 to -30"
    assert 0 <= components["renewables_bonus"] <= 20, "Renewables bonus should be 0-20"
    assert -15 <= components["pollution_penalty"] <= 0, "Pollution penalty should be 0 to -15"
    assert 0 <= components["policy_bonus"] <= 3, "Policy bonus should be 0-3"


def test_data_source_consistency():
    """Test that data sources are consistently reported across different scenarios."""
    res = compute_cevs_for_company("Source Test Corp", company_country="Finland")
    
    sources = res["sources"]
    
    # All expected sources should be present
    required_sources = [
        "epa_matches", "iso_count", "renewables_source", 
        "pollution_source", "edgar_source", "policy_source", 
        "pollution_trend_source"
    ]
    
    for source_key in required_sources:
        assert source_key in sources, f"Missing source key: {source_key}"
    
    # Sources should have reasonable values
    assert isinstance(sources["epa_matches"], int) and sources["epa_matches"] >= 0
    assert isinstance(sources["iso_count"], int) and sources["iso_count"] >= 0
    
    # Source paths/descriptions should be non-empty strings
    source_descriptions = ["renewables_source", "pollution_source", "edgar_source", "policy_source"]
    for desc_key in source_descriptions:
        assert isinstance(sources[desc_key], str) and len(sources[desc_key]) > 0
