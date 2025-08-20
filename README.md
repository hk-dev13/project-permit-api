# 🌍 Environmental Data Verification API

![Badge showing license type Business Source License 1.1 in blue color](https://img.shields.io/badge/License-BSL--1.1-blue.svg) 
![Badge showing usage status Non-Commercial in orange color](https://img.shields.io/badge/Use-Non--Commercial-orange.svg)
![Badge showing re-license to Apache 2.0 scheduled for 2028 in green color](https://img.shields.io/badge/Re--License-Apache%202.0%20(2028)-green.svg)
![Badge showing project status MVP Global in brightblue color](https://img.shields.io/badge/Status-MVP%20Global-brightblue.svg)
![Badge showing build passing in success green color](https://img.shields.io/badge/Build-Passing-success.svg)

---

### 🚀 Turning fragmented environmental data into structured, verifiable insights for businesses, analysts, and ESG investors.

The **Environmental Data Verification API** provides standardized, modular, and multi-source access to global environmental datasets.  
It transforms raw and fragmented data into consistent, actionable insights that can be integrated into business systems, analysis pipelines, and regulatory tools.


# Project Overview

This project aims to provide a structured, unified, and developer-friendly API for environmental data verification.
The main focus is transforming fragmented, raw, and hard-to-access environmental datasets into consistent, normalized insights that are easy to integrate into analytics pipelines, business workflows, and ESG reporting systems.

## Focus & Goals
## Project Focus: Environmental Data Verification

Building an API that presents standardized environmental data accessible across industries and analysis use cases.

## Short-Term Goal: Global MVP

## The project has transitioned from a local focus (KLHK Indonesia) to a global scale. The initial MVP targets include:

✅ Multi-Source Integration → currently connected to EPA Envirofacts (USA) for power plant emissions.

✅ Modular Architecture → restructured into a clean, modular codebase, making it easy to add new data sources (e.g., ISO 14001, EEA).

✅ Data Standardization → normalize diverse datasets into a consistent schema.

✅ Core API Features → search, filtering, pagination, and basic statistics.

## Long-Term Goal: CEVS (Comprehensive Environmental Verification Score)

The project aims to deliver a single holistic environmental performance score (CEVS), aggregating data from multiple trusted sources:

Combine datasets from EPA, EEA, UNEP, ISO

Deliver a single metric (CEVS) valuable for:

ESG Investors

Global Supply Chain Managers

Regulators & Industry Watchdogs  

---

## Features
- ✅ Proxy API ke PTSP KLHK  
- ✅ Caching & pagination  
- ✅ Search by company, type, status  
- ✅ Standardized JSON response  
- ✅ Error handling robust  
- ✅ API Documentation lengkap  
- ✅ Unit test & quick test  

---

## Project Structure
project-permit-api/
├── api/                         # Core API server (Flask)
│   ├── api_server.py            # App entrypoint
│   ├── routes/                  # Blueprints
│   │   ├── health.py
│   │   └── permits.py
│   ├── clients/                 # API clients (shim to legacy for now)
│   │   └── global_client.py
│   └── utils/                   # Shared utilities
│       ├── cache.py             # TTL in-memory cache
│       └── schema.py            # Permit schema & normalizer
│
├── archive/
│   ├── experiments/             # Legacy client and prototypes
│   │   ├── klhk_client_fixed.py
│   │   └── demo_cookies.json
│   └── legacy_scraper/          # Old web scraping scripts (kept for reference)
│       ├── web_scraper.py
│       ├── perizinan_scraper.py
│       └── advanced_scraper.py
│
├── tests/                       # Test scripts
│   ├── test_api.py
│   └── quick_test.py
│
├── output/
├── API_DOCUMENTATION.md
├── PROJECT_SUMMARY.md
├── requirements.txt
├── README.md
└── LICENSE

yaml
Copy
Edit

---

## Getting Started

### 1. Clone repo
```bash
git clone https://github.com/hk-dev13/project-permit-api.git
cd project-permit-api

# Setup environment (Windows)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run API
python api\api_server.py

# Server
# http://127.0.0.1:5000


---

## Authentication & API Keys

This API requires an API key for all `/global/*` endpoints. Permits endpoints are public, but global data and analytics require authentication.

**How to use your API key:**
- Add to the `Authorization` header as `Bearer <your_api_key>` (recommended)
- Or use the `X-API-Key` header
- Or as a query parameter: `?api_key=<your_api_key>` (for testing only)


**API Key Tiers (example):**

| Tier        | Example Key                                             | Rate Limit     | Features                       |
|-------------|--------------------------------------------------------|----------------|---------------------------------|
| Basic       | `basic_xxxxxxxxxx`       | 100/hour       | emissions, countries, basic_stats |
| Premium     | `premium_xxxxxxxxxx`     | 1000/hour      | + stats, analytics, bulk_export |
| Enterprise  | `enterprise_xxxxxxxxxxx` | unlimited      | all features                   |

> **Note:** Production API keys are not published. Please request your key from the admin or support team.

> **Note:** Production API keys are not published. Please request your key from the admin or support team.

**Example request:**

```bash
curl -H "Authorization: Bearer basic_xxxxxxxxxxxx" \
	https://<your-app-runner-url>/global/emissions
```

---

## Live API Documentation (Swagger/OpenAPI)

Interactive API docs are available at:

	https://<your-app-runner-url>/docs

You can try endpoints, see schemas, and view authentication requirements directly in the browser.

---

## Available Endpoints

| Method | Endpoint                  | Description                       |
|--------|---------------------------|-----------------------------------|
| GET    | /                         | API documentation overview        |
| GET    | /health                   | Health check                      |
| GET    | /permits                  | Get all permits (with pagination) |
| GET    | /permits/search           | Search permits by params          |
| GET    | /permits/active           | Get only active permits           |
| GET    | /permits/company/<name>   | Get permits for specific company  |
| GET    | /permits/type/<type>      | Get permits by type               |
| GET    | /permits/stats            | Get permit statistics             |
| GET    | /global/emissions         | [API key] Global emissions data   |
| GET    | /global/iso               | [API key] ISO country data        |
| GET    | /global/eea               | [API key] EEA data                |
| GET    | /global/edgar             | [API key] EDGAR data              |
| GET    | /global/cevs/<company>    | [API key] CEVS score for company  |

See `/docs` for full OpenAPI/Swagger documentation and try-it-out.

---

Detail lengkap ada di API Documentation.

Testing
Quick test:
```bash
python tests\quick_test.py
```

Comprehensive test:
```bash
python tests\test_api.py
```

Documentation
[API Documentation](API_DOCUMENTATION.md) → Endpoint, request/response, examples.

[Project Summary] (PROJECT_SUMMARY.md) → Ringkasan MVP, fitur, roadmap, dan next steps.


## Notes
File output/ dan demo_cookies.json ignored via .gitignore

Untuk production, gunakan Gunicorn + Redis (lihat catatan di API Documentation)

Author
Husni Kusuma (hk-dev13)
Fokus pada Web3, AI, dan Quantum Computing.

Made with ❤️ for data transparency

---

## Data integrations (extended)

- EPA: Envirofacts efservice (configurable via EPA_ENV_BASE/EPA_ENV_TABLE)
- EEA: CSV/JSON renewables and industrial pollutants (EEA_CSV_URL, EEA_RENEWABLES_SOURCE, EEA_POLLUTION_SOURCE)
- ISO: CSV/JSON and Excel list (ISO_CSV_URL, ISO_XLSX_PATH)
- EDGAR: UCDB Excel aggregated per country-year (set EDGAR_XLSX_PATH or place file at `reference/EDGAR_emiss_on_UCDB_2024.xlsx`)

CEVS pollution trend source selection: set `CEVS_POLLUTION_SOURCE` to `auto` (default), `eea`, or `edgar`.

## ✅ Current Status

✅ Completed:

Modular Flask API with Blueprints + CORS
Endpoints:
/, /health
/permits/* (KLHK)
/global/emissions, /global/emissions/stats
/global/iso, /global/eea, /global/edgar
/global/cevs/<company>
Data integrations: EPA/KLHK permits, EEA renewables + pollutants, ISO 14001 (Excel), EDGAR UCDB (Excel + caching)
CEVS Aggregator with modular scoring: base score + bonuses/penalties + clamped [0..100]
Diagnostic endpoint: /global/edgar (country/pollutant trends)
ENV-based source control
Testing: pytest, unit + smoke tests ✅
Documentation: PROJECT_SUMMARY.md and API_DOCUMENTATION.md#   T e s t   G i t H u b   A c t i o n s   t r i g g e r 
 
 