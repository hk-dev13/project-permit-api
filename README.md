# Web Scraping Project - Demonstrasi Python

Proyek ini mendemonstrasikan cara membuat web scraper menggunakan Python untuk mengambil data dari website secara terprogram. Ini adalah proof of concept yang menunjukkan bahwa Anda dapat mengekstrak data secara otomatis dari halaman web.

## 📋 Deskripsi

Web scraping adalah teknik untuk mengekstrak data dari website secara otomatis. Proyek ini menggunakan:

- **requests**: Untuk mengirim HTTP requests dan mengunduh HTML
- **BeautifulSoup**: Untuk parsing dan ekstraksi data dari HTML
- **pandas**: Untuk manipulasi dan export data
- **lxml**: Parser yang lebih cepat untuk BeautifulSoup

## 🚀 Quick Start

### 1. Instalasi Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan Demo Dasar

```bash
python web_scraper.py
```

### 3. Jalankan Demo Perizinan

```bash
python perizinan_scraper.py
```

## 📁 Struktur Project

```
web_scraping_project/
├── README.md                 # Dokumentasi ini
├── requirements.txt          # Dependencies Python
├── web_scraper.py           # Script demo dasar
├── perizinan_scraper.py     # Script demo untuk data perizinan
├── output/                  # Folder hasil scraping (dibuat otomatis)
│   ├── *.csv               # File CSV hasil scraping
│   ├── *.xlsx              # File Excel hasil scraping
│   └── *.json              # File JSON hasil scraping
└── examples/               # Contoh-contoh tambahan
```

## 🔧 Cara Kerja

### Proses Dasar Web Scraping

1. **Identifikasi URL Target**: Tentukan halaman web yang ingin di-scrape
2. **Fetch HTML**: Gunakan `requests` untuk mengunduh kode sumber HTML
3. **Parse HTML**: Gunakan `BeautifulSoup` untuk menganalisis struktur HTML
4. **Ekstrak Data**: Cari dan ambil elemen-elemen yang diinginkan
5. **Simpan Data**: Export ke format terstruktur (CSV, Excel, JSON)

### Contoh Kode Dasar

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. Ambil halaman web
url = "https://example.com"
response = requests.get(url)

# 2. Parse HTML
soup = BeautifulSoup(response.content, 'html.parser')

# 3. Ekstrak data
data = []
for item in soup.find_all('div', class_='data-item'):
    title = item.find('h2').get_text(strip=True)
    description = item.find('p').get_text(strip=True)
    data.append({'title': title, 'description': description})

# 4. Simpan ke CSV
df = pd.DataFrame(data)
df.to_csv('hasil_scraping.csv', index=False)
```

## 📊 Fitur-fitur Script

### Web Scraper Dasar (`web_scraper.py`)

- ✅ Scraping quotes dari quotes.toscrape.com
- ✅ Scraping data buku dari books.toscrape.com
- ✅ Ekstraksi link, tabel, dan konten teks
- ✅ Export ke CSV dengan encoding UTF-8
- ✅ Error handling dan retry mechanism
- ✅ Random delay untuk menghindari rate limiting

### Perizinan Scraper (`perizinan_scraper.py`)

- ✅ Demo scraping tabel dari Wikipedia
- ✅ Contoh struktur data perizinan
- ✅ Export dalam multiple format (CSV, Excel, JSON)
- ✅ Analisis struktur halaman web
- ✅ Robust error handling
- ✅ Session management dengan proper headers

## 🎯 Untuk Website Perizinan KLHK

Untuk mengaplikasikan pada website perizinan KLHK yang sebenarnya, Anda perlu:

### 1. Analisis Target Website

```python
# Contoh analisis struktur halaman
scraper = PerizinanScraper()
analysis = scraper.analyze_webpage_structure("https://target-website.com")
print(analysis)
```

### 2. Identifikasi Elemen Target

- Inspeksi elemen HTML menggunakan Developer Tools browser
- Cari tabel atau div yang berisi data perizinan
- Catat class, id, atau selector CSS yang tepat

### 3. Handling Khusus

- **Login Form**: Jika memerlukan login
- **CAPTCHA**: Jika ada sistem anti-bot
- **Pagination**: Jika data tersebar di multiple halaman
- **AJAX Loading**: Jika data dimuat via JavaScript

### Contoh untuk KLHK

```python
def scrape_klhk_permits(self):
    """
    Template untuk scraping data perizinan KLHK
    Perlu disesuaikan dengan struktur website yang sebenarnya
    """
    base_url = "https://klhk.go.id/rekap-perizinan"  # URL contoh
    
    response = self.fetch_page_with_retry(base_url)
    if not response:
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Sesuaikan selector berdasarkan struktur HTML yang sebenarnya
    permit_table = soup.find('table', class_='permit-table')  # Contoh selector
    
    permits_data = []
    if permit_table:
        rows = permit_table.find_all('tr')[1:]  # Skip header
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 6:  # Sesuaikan dengan jumlah kolom
                permit_data = {
                    'no_izin': cells[0].get_text(strip=True),
                    'nama_perusahaan': cells[1].get_text(strip=True),
                    'jenis_izin': cells[2].get_text(strip=True),
                    'tanggal_terbit': cells[3].get_text(strip=True),
                    'status': cells[4].get_text(strip=True),
                    'lokasi': cells[5].get_text(strip=True)
                }
                permits_data.append(permit_data)
    
    return permits_data
```

## ⚠️ Penting - Etika Web Scraping

### DO's ✅

- Selalu cek `robots.txt` website target
- Gunakan delay yang wajar antar request (1-2 detik)
- Respect website's Terms of Service
- Gunakan User-Agent yang proper
- Jangan overload server target
- Simpan data dengan cara yang bertanggung jawab

### DON'Ts ❌

- Jangan scrape data pribadi atau sensitif
- Jangan bypass sistem keamanan
- Jangan mengabaikan rate limiting
- Jangan scrape data yang dilindungi copyright
- Jangan gunakan data untuk tujuan ilegal

## 🔍 Troubleshooting

### Error: "Connection refused"
- Cek koneksi internet
- Website mungkin memblokir bot
- Coba gunakan proxy atau VPN

### Error: "Data tidak ditemukan"
- Periksa selector CSS/XPath
- Website mungkin berubah struktur
- Data mungkin dimuat via JavaScript (perlu Selenium)

### Error: "403 Forbidden"
- Gunakan User-Agent yang valid
- Website mungkin butuh cookies/session
- Implementasi rate limiting

## 📝 Pengembangan Lanjutan

### Untuk Scraping yang Lebih Complex

1. **Selenium WebDriver**: Untuk JavaScript-heavy websites
```bash
pip install selenium
```

2. **Scrapy Framework**: Untuk projek scraping besar
```bash
pip install scrapy
```

3. **Proxy Integration**: Untuk menghindari IP blocking
```python
proxies = {'http': 'http://proxy-server:port'}
requests.get(url, proxies=proxies)
```

## 📧 Support

Jika menemukan masalah atau butuh bantuan:

1. Periksa log error di console
2. Cek apakah dependencies sudah terinstall dengan benar
3. Pastikan koneksi internet stabil
4. Baca dokumentasi BeautifulSoup dan requests

## 📄 Lisensi

Proyek ini untuk tujuan edukatif dan demonstrasi. Pastikan mematuhi terms of service website target saat menggunakan script ini.

---

**Happy Scraping! 🕷️**
