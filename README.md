# project-permit-api 🚀

Flask API Proxy untuk data perizinan PTSP KLHK.  
Proyek ini awalnya dimulai sebagai **Web Scraping Project** untuk mengambil data dari website, namun kemudian dikembangkan menjadi **API Proxy berbasis Flask** karena adanya endpoint API resmi.

---

## 📋 Deskripsi

API Proxy ini berfungsi sebagai middleware untuk:
- Mengambil data dari API PTSP KLHK
- Menyediakan endpoint CRUD dasar
- Menambahkan mekanisme caching & validasi input
- Menyediakan dokumentasi & health check endpoint

---

## 🚀 Quick Start

### 1. Instalasi Dependencies
```bash
pip install -r requirements.txt
