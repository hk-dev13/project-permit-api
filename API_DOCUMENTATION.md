# Environmental Data Verification API - Documentation

📑 Quick Links
- [🌍 Project Summary](PROJECT_SUMMARY.md) 
- [📘 Main README](README.md)
- [🚀 Performance Improvements](PERFORMANCE_IMPROVEMENTS.md)

An API that delivers standardized environmental data with **secure access control** and **rate limiting**, accessible across industries and analysis use cases.

## 📋 Overview

This API acts as a proxy/aggregator between your applications and multiple official data sources (EPA, EEA, UNEP, ISO, KLHK). It provides:

✅ **Secure API Key Authentication**
✅ **Dynamic Rate Limiting** based on tier  
✅ **Comprehensive Caching** for better performance
✅ **Data filtering & preprocessing**
✅ **Country name normalization** across sources
✅ **Standardized response format**
✅ **Pagination for large datasets**
✅ **Robust error handling**
✅ **Docker deployment ready**

## 🔐 Authentication & API Keys

### Getting Your API Key

**For Development/Testing:**
Use the demo keys provided:
- **Basic Tier**: `demo_key_basic_2025` (30 requests/minute)
- **Premium Tier**: `demo_key_premium_2025` (100 requests/minute)

**For Production:**
Contact the API administrator to get your production API key.

### Using Your API Key

Include your API key in requests using one of these methods:

#### Method 1: Authorization Header (Recommended)
```bash
curl -H "Authorization: Bearer your_api_key_here" \
  "http://localhost:5000/global/emissions"
```

#### Method 2: X-API-Key Header  
```bash
curl -H "X-API-Key: your_api_key_here" \
  "http://localhost:5000/global/emissions"
```

#### Method 3: Query Parameter (Development Only)
```bash
curl "http://localhost:5000/global/emissions?api_key=your_api_key_here"
```

### Rate Limits by Tier

| Tier | Requests/minute | Use Case |
|------|----------------|----------|
| Basic | 30 | Development, testing, light usage |  
| Premium | 100 | Production applications, heavy usage |
| Master | 200 | Administrative access |

## 🚀 Getting Started

### Prerequisites
```bash
pip install flask flask-cors flask-limiter python-dotenv requests beautifulsoup4 pandas pyarrow
```

### Environment Setup
1. Copy the environment template:
```bash
cp .env.example .env
```

2. Update `.env` with your configuration:
```env
API_KEYS=your_api_key:YourApp:basic
MASTER_API_KEY=your_secure_master_key
```

### Running the Server

#### Local Development
```bash
python api/api_server.py
```

#### Docker (Recommended for Production)
```bash
# Build and run
docker-compose up --build

# Or manually:
docker build -t permit-api .
docker run -p 5000:5000 permit-api
```

## 🌐 Base URL
- **Local**: `http://localhost:5000`
- **Docker**: `http://localhost:5000` 

## 📡 API Endpoints

### Public Endpoints (No API Key Required)

#### 1. API Information
**GET** `/`

Returns basic metadata about the API.

**Response:**

{
  "name": "Environmental Data Verification API",
  "version": "1.0.0",
  "description": "API proxy for accessing environmental permit and emission datasets",
  "endpoints": { ... },
  "usage_examples": { ... }
}

#### 2. Health Check
**GET** `/health`

Returns API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-19T10:30:00Z",
  "version": "1.0.0"
}
```

### Protected Endpoints (API Key Required)

All `/global/*` and `/admin/*` endpoints require a valid API key. Include your API key using one of the authentication methods shown above.

#### 3. Global Emissions Data (EPA)
**GET** `/global/emissions`

Returns EPA power plant emissions data with filtering and pagination.

**Authentication:** Required  
**Rate Limit:** Based on your tier (30-200 requests/minute)

**Query Parameters:**
- `state` (optional): Filter by US state (e.g., "CA", "TX")
- `year` (optional): Filter by year (e.g., 2023) 
- `pollutant` (optional): Filter by pollutant type (e.g., "CO2", "NOx")
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 50, max: 100)

**Example Request:**
```bash
curl -H "Authorization: Bearer demo_key_basic_2025" \
  "http://localhost:5000/global/emissions?state=CA&year=2023&limit=10"
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "facility_name": "Example Power Plant",
      "state": "CA", 
      "year": 2023,
      "pollutant": "CO2",
      "emissions": 1500000.0,
      "unit": "tons"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 245
  },
  "retrieved_at": "2025-08-19T10:30:00Z"
}
```

#### 4. Emissions Statistics  
**GET** `/global/emissions/stats`

Returns aggregated emissions statistics.

**Authentication:** Required

**Response:**
```json
{
  "status": "success", 
  "data": {
    "total_facilities": 1250,
    "total_emissions": 125000000.0,
    "by_state": {"CA": 15000000, "TX": 22000000},
    "by_pollutant": {"CO2": 100000000, "NOx": 25000000}
  }
}
```

#### 5. ISO 14001 Certifications
**GET** `/global/iso`

Returns ISO 14001 environmental certification data.

**Authentication:** Required  

**Query Parameters:**
- `country` (optional): Filter by country (e.g., "Sweden", "USA", "DE")
- `limit` (optional): Maximum results (default: 100)

**Example Request:**
```bash
curl -H "X-API-Key: demo_key_premium_2025" \
  "http://localhost:5000/global/iso?country=Sweden&limit=20"
```

#### 6. EEA Environmental Indicators
**GET** `/global/eea`

Returns European Environment Agency data from Parquet sources.

**Authentication:** Required

**Query Parameters:**
- `country` (optional): Filter by country name
- `indicator` (optional): Indicator type ("GHG", "renewable", "pollution") 
- `year` (optional): Filter by year
- `limit` (optional): Maximum results (default: 50)

#### 7. EDGAR Emissions Data  
**GET** `/global/edgar`

Returns EDGAR urban emissions data with trend analysis.

**Authentication:** Required

**Query Parameters:**
- `country` (required): Country name (normalized automatically)
- `pollutant` (optional): Pollutant type (default: "PM2.5")  
- `window` (optional): Trend analysis window in years (default: 3)

#### 8. CEVS Composite Score
**GET** `/global/cevs/<company>`

Returns Composite Environmental Verification Score combining EPA, ISO, EEA, and EDGAR data.

**Authentication:** Required

**Path Parameters:**
- `company` (required): Company name

**Query Parameters:**  
- `country` (optional): Company's country for localized analysis

**Response:**
```json
{
  "status": "success",
  "data": {
    "company": "Green Energy Co",
    "cevs_score": 85.6,
    "components": {
      "epa_score": 70.2,
      "iso_bonus": 15.0, 
      "eea_renewable_bonus": 8.4,
      "edgar_pollution_penalty": -8.0
    },
    "sources": ["EPA", "ISO", "EEA", "EDGAR"],
    "country_context": "Sweden"
  }
}
```

### Administrative Endpoints

#### 9. List API Keys (Admin)
**GET** `/admin/api-keys`

Lists all registered API keys (premium tier required).

#### 10. Create API Key (Admin)  
**POST** `/admin/api-keys`

Creates a new API key (premium tier required).

#### 11. API Usage Statistics (Admin)
**GET** `/admin/stats`

Returns API usage statistics (premium tier required).

## Legacy Endpoints (No API Key Required)

These endpoints remain open for backward compatibility:

- `/permits` - Indonesian permit data (KLHK PTSP)
- `/permits/search` - Search Indonesian permits

## 🔧 Technical Features

### Country Name Normalization

The API automatically normalizes country names across all data sources for consistent data joining:

- **Input**: "USA", "United States", "US" → **Normalized**: "united_states"  
- **Input**: "Deutschland", "Germany", "DE" → **Normalized**: "germany"
- **Input**: "Czech Republic", "Czechia", "CZ" → **Normalized**: "czech_republic"

**Supported variants**: 50+ countries with 267+ name variations including:
- Official names, common names, abbreviations
- ISO codes (2-letter and 3-letter)
- Alternative spellings and regional variants

### Caching & Performance

- **EEA Client**: LRU cache for Parquet downloads (10 items)
- **ISO Client**: LRU cache for file operations (5-10 items)  
- **EDGAR Client**: Global instance-level caching for Excel data
- **Response caching**: 30s-5min depending on data freshness

### Error Handling

**Authentication Errors:**
```json
{
  "status": "error",
  "message": "API key required. Include it in Authorization header...",
  "code": "MISSING_API_KEY",
  "demo_keys": {
    "basic": "demo_key_basic_2025", 
    "premium": "demo_key_premium_2025"
  }
}
```

**Rate Limit Errors:**
```json
{
  "status": "error",
  "message": "Rate limit exceeded: 30 per minute",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

**Data Errors:**
```json
{
  "status": "error", 
  "message": "Country 'XYZ' not found in dataset",
  "code": "DATA_NOT_FOUND"
}
```

### Security Headers

The API includes security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`  
- `X-XSS-Protection: 1; mode=block`

## 🚀 Deployment

### Docker Deployment (Recommended)

```bash
# Clone repository
git clone https://github.com/your-org/project-permit-api.git
cd project-permit-api

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Build and deploy
docker-compose up -d --build

# Check health
curl http://localhost:5000/health
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=api.api_server:app
export FLASK_ENV=production
export API_KEYS="your_key:YourApp:basic"

# Run server
python -m flask run --host=0.0.0.0 --port=5000
```

### Environment Variables

See `.env.example` for full configuration options including:
- API keys and authentication settings
- Database connections (PostgreSQL, Redis)
- Rate limiting configuration  
- CORS and security settings
- Logging levels

## ⚡ Performance Tips

1. **Use Premium Keys**: Get 100 requests/minute vs 30 for basic
2. **Cache Responses**: API includes cache headers - respect them
3. **Batch Requests**: Use pagination efficiently 
4. **Specific Filters**: Use country/year filters to reduce response size
5. **Proper Headers**: Always use Authorization header vs query params

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/your-org/project-permit-api/issues)
- **API Questions**: Create an issue with "API" label
- **Production Keys**: Contact your administrator


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