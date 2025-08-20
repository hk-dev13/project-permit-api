from __future__ import annotations

import os # <-- DITAMBAHKAN
import json
from api.services.cevs_aggregator import compute_cevs_for_company
from flask import Flask
from api.api_server import app as flask_app


def test_global_edgar_endpoint_smoke(monkeypatch):
    # Use Flask test client to avoid needing a running server
    client = flask_app.test_client()

    # Ambil API key dari environment variable
    api_key = os.getenv('API_KEY')
    # PENTING: Ganti 'X-API-KEY' jika nama header Anda berbeda
    headers = {'X-API-KEY': api_key}

    resp = client.get("/global/edgar?country=United%20States&pollutant=PM2.5&window=3", headers=headers) # <-- DITAMBAHKAN headers
    
    # Karena API Key sudah valid, status code tidak akan 401 lagi.
    # Tes ini sekarang memeriksa apakah statusnya 200 (sukses) atau 400 (jika ada parameter salah)
    assert resp.status_code in (200, 400)
    data = resp.get_json()
    assert isinstance(data, dict)
    if resp.status_code == 200:
        assert data.get("status") == "success"
        assert "series" in data and isinstance(data["series"], list)
        assert "trend" in data and isinstance(data["trend"], dict)

# Bagian di bawah ini untuk testing lokal dan tidak dijalankan oleh pytest
# jadi tidak perlu diubah.
"""
Quick test script untuk API tanpa perlu terminal interaktif
"""

import requests


def test_api_endpoints():
    base_url = "http://127.0.0.1:5000"

    endpoints = [
        "/",
        "/health",
        "/permits",
        "/permits/search?nama=PT",
        "/permits/company/PT%20Semen%20Indonesia",
        "/permits/stats",
    ]

    print("🧪 Quick API Test")
    print("=" * 50)

    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n🔍 Testing: {endpoint}")

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success - Status: {response.status_code}")

                if "data" in data and isinstance(data["data"], list):
                    print(f"   Records: {len(data['data'])}")
                elif "statistics" in data:
                    stats = data["statistics"]
                    print(f"   Total permits: {stats.get('total_permits', 'N/A')}")
                elif "status" in data:
                    print(f"   API Status: {data['status']}")

            else:
                print(f"❌ Failed - Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")

    print("\n" + "=" * 50)
    print("Test complete!")


if __name__ == "__main__":
    test_api_endpoints()
