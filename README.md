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
├── api/ # Core API server (Flask)
│ ├── api_server.py
│ ├── klhk_client.py
│ └── test_api.py
│
├── legacy_scraper/ # Old web scraping scripts (for reference)
│ ├── web_scraper.py
│ ├── perizinan_scraper.py
│ └── advanced_scraper.py
│
├── experiments/ # Quick test & prototype scripts
│ ├── quick_test.py
│ ├── klhk_client_fixed.py
│ └── demo_cookies.json
│
├── output/ # Generated data (ignored in git)
│
├── API_DOCUMENTATION.md # Detail API endpoints
├── PROJECT_SUMMARY.md # Project overview & roadmap
├── requirements.txt # Dependencies
├── README.md # This file
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
2. Setup environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
3. Jalankan API
bash
Copy
Edit
python api/api_server.py
Server akan berjalan di:
 http://127.0.0.1:5000

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

bash
Copy
Edit
python experiments/quick_test.py
Comprehensive test:

bash
Copy
Edit
pytest api/test_api.py

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