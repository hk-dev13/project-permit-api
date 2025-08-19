"""
Test suite for global API routes to ensure all endpoints return proper responses.
This provides a safety net for core functionality.
"""
from __future__ import annotations

import pytest
from flask import Flask
from api.api_server import app as flask_app


class TestGlobalRoutes:
    """Test all /global/* endpoints for basic functionality and response structure."""

    @pytest.fixture
    def client(self):
        """Flask test client for making API requests."""
        return flask_app.test_client()

    def test_global_emissions_basic_response(self, client):
        """Test /global/emissions returns 200 and proper structure."""
        resp = client.get("/global/emissions?limit=5")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

    def test_global_emissions_with_filters(self, client):
        """Test /global/emissions with state and year filters."""
        resp = client.get("/global/emissions?state=TX&year=2023&limit=3")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert data["filters"]["state"] == "TX"
        assert data["filters"]["year"] == 2023

    def test_global_emissions_stats(self, client):
        """Test /global/emissions/stats returns aggregated statistics."""
        resp = client.get("/global/emissions/stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert "statistics" in data
        stats = data["statistics"]
        assert "by_state" in stats
        assert "by_pollutant" in stats
        assert "by_year" in stats
        assert "total_records" in stats

    def test_global_iso_basic_response(self, client):
        """Test /global/iso returns 200 and proper structure."""
        resp = client.get("/global/iso?limit=10")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_global_iso_with_country_filter(self, client):
        """Test /global/iso with country filter."""
        resp = client.get("/global/iso?country=Germany&limit=5")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert data["filters"]["country"] == "Germany"

    def test_global_eea_basic_response(self, client):
        """Test /global/eea returns 200 and proper structure."""
        resp = client.get("/global/eea?limit=10")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_global_eea_with_filters(self, client):
        """Test /global/eea with indicator, country, and year filters."""
        resp = client.get("/global/eea?country=Sweden&indicator=GHG&year=2023&limit=5")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        filters = data["filters"]
        assert filters["country"] == "Sweden"
        assert filters["indicator"] == "GHG"
        assert filters["year"] == 2023

    def test_global_cevs_basic_company(self, client):
        """Test /global/cevs/{company} returns proper CEVS score structure."""
        resp = client.get("/global/cevs/Green%20Energy%20Corp")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert "score" in data
        assert "components" in data
        assert "sources" in data
        assert "details" in data
        
        # Validate score is within expected range
        assert 0 <= data["score"] <= 100
        
        # Validate components structure
        components = data["components"]
        expected_components = ["base", "iso_bonus", "epa_penalty", "renewables_bonus", "pollution_penalty", "policy_bonus"]
        for comp in expected_components:
            assert comp in components

    def test_global_cevs_with_country(self, client):
        """Test /global/cevs/{company} with country parameter for enhanced scoring."""
        resp = client.get("/global/cevs/Swedish%20Wind%20Power?country=Sweden")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert data["country"] == "Sweden"
        
        # Should have renewable energy data for Sweden
        details = data["details"]
        assert "renewables" in details
        if details["renewables"]["country_row"]:
            assert details["renewables"]["country_row"]["country"].lower() == "sweden"

    def test_global_edgar_basic_response(self, client):
        """Test /global/edgar returns proper structure (may have empty data if file missing)."""
        resp = client.get("/global/edgar?country=United%20States&pollutant=PM2.5")
        assert resp.status_code == 200  # Should not fail even if EDGAR file missing
        data = resp.get_json()
        assert data["status"] == "success"
        assert "country" in data
        assert "pollutant" in data
        assert "series" in data
        assert "trend" in data
        assert data["country"] == "United States"
        assert data["pollutant"] == "PM2.5"

    def test_global_edgar_missing_country(self, client):
        """Test /global/edgar returns 400 when country parameter is missing."""
        resp = client.get("/global/edgar?pollutant=NOx")
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["status"] == "error"
        assert "country is required" in data["message"]

    def test_global_edgar_with_window_parameter(self, client):
        """Test /global/edgar with custom trend window parameter."""
        resp = client.get("/global/edgar?country=Germany&pollutant=NOx&window=5")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        # Trend should reflect the window parameter in its calculation
        trend = data["trend"]
        assert "pollutant" in trend
        assert trend["pollutant"] == "NOx"
