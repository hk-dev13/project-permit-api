# KLHK Permit API Proxy - Documentation

API proxy untuk mengakses data perizinan dari PTSP (Pelayanan Terpadu Satu Pintu) Kementerian Lingkungan Hidup dan Kehutanan (KLHK) Indonesia.

## 📋 Overview

API ini bertindak sebagai **proxy/perantara** antara aplikasi Anda dengan API resmi PTSP MENLHK. API ini menyediakan:

- ✅ **Caching** untuk performa yang lebih baik
- ✅ **Data filtering** dan preprocessing
- ✅ **Standardized response format**
- ✅ **Pagination** untuk dataset besar  
- ✅ **Error handling** yang robust
- ✅ **Search functionality** yang fleksibel

## 🚀 Getting Started

### Prerequisites

```bash
pip install flask flask-cors requests beautifulsoup4 pandas
```

### Running the Server

```bash
python api_server.py
```

Server akan berjalan di `http://localhost:5000`

## 📡 Base URL

```
http://localhost:5000
```

## Endpoints

### 1. API Information
**GET** `/`

Mendapatkan informasi dasar tentang API.

**Response:**
```json
{

### Global (EPA/EEA/ISO/EDGAR) Endpoints

- `/global/emissions` — EPA power plant emissions (filters: state, year, pollutant, page, limit)
- `/global/emissions/stats` — Aggregated stats (by state, pollutant, year)
- `/global/iso` — ISO 14001 certifications (filters: country, limit)
- `/global/eea` — EEA indicators (CSV/JSON-backed)
- `/global/cevs/<company>` — Composite score using EPA, ISO, EEA, and EDGAR (country optional)

Notes:
- EDGAR UCDB Excel can be set via `EDGAR_XLSX_PATH`; trends used for PM2.5/NOx at country level.
- Pollution trend source is selectable via `CEVS_POLLUTION_SOURCE` = `auto` (default), `eea`, or `edgar`.
  "name": "KLHK Permit API Proxy",
  "version": "1.0.0", 
  "description": "API proxy untuk mengakses data perizinan PTSP MENLHK",
  "endpoints": { ... },
  "usage_examples": { ... }
}
```

### 2. Health Check
**GET** `/health`

Check status kesehatan server dan cache.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "cache_status": "active",
  "last_updated": "2024-01-15T10:25:00"
}
```

### 3. Get All Permits
**GET** `/permits`

Mendapatkan semua data perizinan dengan pagination optional.

**Query Parameters:**
- `page` (optional): Nomor halaman (default: 1)
- `limit` (optional): Jumlah record per halaman (default: 50, max: 100)

**Example:**
```
GET /permits?page=1&limit=10
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "nama_perusahaan": "PT. Semen Indonesia (Persero) Tbk",
      "alamat": "Jl. Veteran No. 9, Gresik, Jawa Timur",
      "jenis_layanan": "Izin Lingkungan",
      "nomor_sk": "SK.123/KLHK/2024",
      "tanggal_berlaku": "2024-01-15",
      "judul_kegiatan": "Operasional Pabrik Semen",
      "status": "Aktif",
      "retrieved_at": "2024-01-15T10:30:00",
      "source": "PTSP MENLHK"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 100,
    "total_pages": 10,
    "has_next": true,
    "has_prev": false
  },
  "retrieved_at": "2024-01-15T10:30:00"
}
```

### 4. Search Permits
**GET** `/permits/search`

Mencari perizinan berdasarkan berbagai parameter.

**Query Parameters:**
- `nama` (optional): Nama perusahaan
- `jenis` (optional): Jenis layanan/perizinan
- `status` (optional): Status perizinan

*Minimal 1 parameter harus diisi.*

**Example:**
```
GET /permits/search?nama=PT%20Pertamina&status=Aktif
```

**Response:**
```json
{
  "status": "success",
  "data": [ ... ],
  "search_params": {
    "nama": "PT Pertamina",
    "jenis": "",
    "status": "Aktif"
  },
  "total_found": 5,
  "retrieved_at": "2024-01-15T10:30:00"
}
```

### 5. Get Active Permits
**GET** `/permits/active`

Mendapatkan hanya perizinan yang statusnya aktif.

**Response:**
```json
{
  "status": "success",
  "data": [ ... ],
  "total_active": 85,
  "total_all": 100,
  "retrieved_at": "2024-01-15T10:30:00"
}
```

### 6. Get Permits by Company
**GET** `/permits/company/<company_name>`

Mendapatkan semua perizinan untuk perusahaan tertentu.

**Example:**
```
GET /permits/company/PT%20Semen%20Indonesia
```

**Response:**
```json
{
  "status": "success",
  "data": [ ... ],
  "company_name": "PT Semen Indonesia",
  "total_found": 3,
  "retrieved_at": "2024-01-15T10:30:00"
}
```

### 7. Get Permits by Type
**GET** `/permits/type/<permit_type>`

Mendapatkan perizinan berdasarkan jenis/tipe tertentu.

**Example:**
```
GET /permits/type/Izin%20Lingkungan
```

**Response:**
```json
{
  "status": "success", 
  "data": [ ... ],
  "permit_type": "Izin Lingkungan",
  "total_found": 25,
  "retrieved_at": "2024-01-15T10:30:00"
}
```

### 8. Get Statistics
**GET** `/permits/stats`

Mendapatkan statistik data perizinan.

**Response:**
```json
{
  "status": "success",
  "statistics": {
    "total_permits": 100,
    "active_permits": 85,
    "inactive_permits": 15,
    "by_permit_type": {
      "Izin Lingkungan": 30,
      "Izin Pembuangan Limbah": 25,
      "Izin AMDAL": 20,
      "Izin Usaha Daur Ulang": 15,
      "Izin Emisi": 10
    },
    "by_status": {
      "Aktif": 85,
      "Dalam Review": 10,
      "Tidak Aktif": 5
    }
  },
  "retrieved_at": "2024-01-15T10:30:00"
}
```

## 📊 Data Schema

### Permit Object
```json
{
  "nama_perusahaan": "string",      // Nama perusahaan
  "alamat": "string",               // Alamat perusahaan  
  "jenis_layanan": "string",        // Jenis perizinan
  "nomor_sk": "string",             // Nomor SK/surat keputusan
  "tanggal_berlaku": "string",      // Tanggal berlaku (YYYY-MM-DD)
  "judul_kegiatan": "string",       // Deskripsi kegiatan
  "status": "string",               // Status perizinan
  "retrieved_at": "string",         // Timestamp pengambilan data (ISO 8601)
  "source": "string"                // Sumber data
}
```

## 🔍 Usage Examples

### Python Example

```python
import requests
import json

# Base URL
base_url = "http://localhost:5000"

# 1. Get all permits
response = requests.get(f"{base_url}/permits")
data = response.json()
print(f"Total permits: {data['pagination']['total_records']}")

# 2. Search for a company
company_name = "PT Pertamina"
response = requests.get(f"{base_url}/permits/search", 
                       params={'nama': company_name})
data = response.json()
print(f"Found {data['total_found']} permits for {company_name}")

# 3. Get statistics
response = requests.get(f"{base_url}/permits/stats")
stats = response.json()['statistics']
print(f"Active permits: {stats['active_permits']}/{stats['total_permits']}")
```

### JavaScript Example

```javascript
const baseUrl = 'http://localhost:5000';

// 1. Get permits with pagination
async function getPermits(page = 1, limit = 10) {
    const response = await fetch(`${baseUrl}/permits?page=${page}&limit=${limit}`);
    const data = await response.json();
    return data;
}

// 2. Search permits
async function searchPermits(companyName) {
    const response = await fetch(`${baseUrl}/permits/search?nama=${encodeURIComponent(companyName)}`);
    const data = await response.json();
    return data;
}

// 3. Get active permits only
async function getActivePermits() {
    const response = await fetch(`${baseUrl}/permits/active`);
    const data = await response.json();
    return data;
}
```

### cURL Examples

```bash
# Get API information
curl http://localhost:5000/

# Get permits with pagination
curl "http://localhost:5000/permits?page=1&limit=5"

# Search by company name
curl "http://localhost:5000/permits/search?nama=PT%20Semen"

# Get permits for specific company
curl "http://localhost:5000/permits/company/PT%20Pertamina"

# Get environmental permits
curl "http://localhost:5000/permits/type/Izin%20Lingkungan"

# Get statistics
curl http://localhost:5000/permits/stats

# Health check
curl http://localhost:5000/health
```

## ⚠️ Error Handling

### Error Response Format
```json
{
  "status": "error",
  "message": "Error description"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request (missing parameters) |
| 404  | Endpoint not found |
| 500  | Internal server error |

### Error Examples

**Missing search parameters:**
```json
{
  "status": "error",
  "message": "At least one search parameter required (nama, jenis, or status)"
}
```

**Invalid endpoint:**
```json
{
  "status": "error", 
  "message": "Endpoint not found",
  "available_endpoints": [
    "/",
    "/health",
    "/permits",
    "..."
  ]
}
```

## 🚀 Performance & Caching

- **Cache Duration**: 1 hour (3600 seconds)
- **Cache Strategy**: In-memory caching (Redis recommended for production)
- **Data Source**: PTSP MENLHK API dengan fallback ke sample data
- **Response Time**: Typically < 100ms untuk cached data

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 5000 | Server port |
| `DEBUG` | True | Debug mode |
| `CACHE_DURATION` | 3600 | Cache duration in seconds |

### Production Deployment

```bash
# Set production environment
export DEBUG=False
export PORT=80

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:80 api_server:app
```

## 📈 Monitoring & Logging

API mencatat log untuk:
- Incoming requests
- Cache hits/misses  
- KLHK API calls
- Errors and exceptions

Log level dapat dikonfigurasi melalui logging configuration.

## 🔒 Security Notes

- API tidak memerlukan authentication (read-only public data)
- CORS enabled untuk cross-origin requests
- Rate limiting belum diimplementasikan (recommended untuk production)
- Input validation untuk query parameters

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Add tests untuk fitur baru
4. Submit pull request

## 📞 Support

Untuk pertanyaan atau masalah:
1. Check dokumentasi ini
2. Run health check endpoint
3. Check server logs
4. Validate input parameters

## 📝 Changelog

### v1.0.0
- Initial release
- Basic CRUD endpoints
- Search functionality
- Caching mechanism
- Error handling
- Documentation

---

**Made with ❤️ for KLHK data transparency**
