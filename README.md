# Project Permit API (MVP KLHK Proxy)

Backend service untuk mengakses **data perizinan PTSP KLHK**.  
Project ini awalnya dimulai dari **web scraping** lalu dikembangkan menjadi **MVP API Proxy berbasis Flask** dengan caching, search, filtering, dan dokumentasi lengkap.  

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

 Available Endpoints
Method	Endpoint	Description
GET	/	API documentation overview
GET	/health	Health check
GET	/permits	Get all permits (with pagination)
GET	/permits/search	Search permits by params
GET	/permits/active	Get only active permits
GET	/permits/company/<name>	Get permits for specific company
GET	/permits/type/<type>	Get permits by type
GET	/permits/stats	Get permit statistics

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

Contributing
Fork repo ini

Buat branch baru feature/nama-fitur

Commit dengan jelas (feat: ..., fix: ...)

Push dan buat Pull Request ke main

Detail aturan kontribusi bisa ditambahkan di CONTRIBUTING.md (coming soon).

Notes
File output/ dan demo_cookies.json ignored via .gitignore

Untuk production, gunakan Gunicorn + Redis (lihat catatan di API Documentation)

Author
Husni Kusuma (hk-dev13)
Fokus pada Web3, AI, dan Quantum Computing.

Made with ❤️ for data transparency