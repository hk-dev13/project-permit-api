# Environmental Data Verification API - Documentation

📑 See also:

📑 Quick Links
- [🌍 Project Summary](PROJECT_SUMMARY.md)
- [📘 Main README](README.md)


An API that delivers standardized environmental data, accessible across industries and analysis use cases.

📋 Overview

This API acts as a proxy/aggregator between your applications and multiple official data sources (EPA, EEA, UNEP, ISO, KLHK). It provides:

✅ Caching for better performance

✅ Data filtering & preprocessing

✅ Standardized response format

✅ Pagination for large datasets

✅ Robust error handling

✅ Flexible search functionality

## Getting Started
Prerequisites
pip install flask flask-cors requests beautifulsoup4 pandas

## Running the Server
python api/api_server.py

## Server will run at:
http://localhost:5000

## Base URL
http://localhost:5000

Endpoints
1. API Information

GET /

Returns basic metadata about the API.

Response:

{
  "name": "Environmental Data Verification API",
  "version": "1.0.0",
  "description": "API proxy for accessing environmental permit and emission datasets",
  "endpoints": { ... },
  "usage_examples": { ... }
}

## Global Endpoints (EPA / EEA / ISO / EDGAR)

/global/emissions — EPA power plant emissions (filters: state, year, pollutant, page, limit)

/global/emissions/stats — Aggregated stats (by state, pollutant, year)

/global/iso — ISO 14001 certifications (filters: country, limit)

/global/eea — EEA indicators (CSV/JSON-backed)

/global/cevs/<company> — Composite CEVS score combining EPA, ISO, EEA, and EDGAR


## Notes:

EDGAR UCDB Excel is configured via EDGAR_XLSX_PATH.

Pollution trend source can be selected via CEVS_POLLUTION_SOURCE = auto | eea | edgar.

## Data Schema
Permit Object
{
  "nama_perusahaan": "string",      
  "alamat": "string",               
  "jenis_layanan": "string",        
  "nomor_sk": "string",             
  "tanggal_berlaku": "string",      
  "judul_kegiatan": "string",       
  "status": "string",               
  "retrieved_at": "string",         
  "source": "string"                
}

## Usage Examples
Python Example
import requests
base_url = "http://localhost:5000"

# Get permits
r = requests.get(f"{base_url}/permits")
print(r.json())

# Search company
r = requests.get(f"{base_url}/permits/search", params={'nama': 'PT Pertamina'})
print(r.json())

# Get statistics
r = requests.get(f"{base_url}/permits/stats")
print(r.json())

## JavaScript Example
const baseUrl = 'http://localhost:5000';

async function getPermits(page = 1, limit = 10) {
  const res = await fetch(`${baseUrl}/permits?page=${page}&limit=${limit}`);
  return res.json();
}

## cURL Example
# Get health status
curl http://localhost:5000/health

# Get all permits
curl "http://localhost:5000/permits?page=1&limit=5"

# Search company
curl "http://localhost:5000/permits/search?nama=PT%20Pertamina"


## Error Handling

Standard Error Response:

{
  "status": "error",
  "message": "Error description"
}

Code	Description
200	Success
400	Bad Request (missing params)
404	Endpoint not found
500	Internal server error


## Performance & Caching

Cache duration: 1 hour

Strategy: In-memory (Redis recommended for production)

Response time: <100ms for cached data


## Configuration
Environment Variables
Variable	Default	Description
PORT	5000	Server port
DEBUG	True	Debug mode
CACHE_DURATION	3600	Cache duration (sec)


## Monitoring & Logging

Logs include: requests, cache hits/misses, upstream API calls, errors.


## Security Notes

Public, read-only API (no auth required)

CORS enabled

Rate limiting recommended for production

Input validation for query params



## Contributing

Fork repo

Create feature branch

Add tests

Submit PR


## 📝 Changelog
v1.0.0

Initial release

CRUD endpoints

Search, filtering, pagination

Caching

Error handling

Documentation

Made with ❤️ for environmental data transparency