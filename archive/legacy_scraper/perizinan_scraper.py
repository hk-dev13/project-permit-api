"""
Contoh Web Scraping untuk Data Perizinan
Script ini mendemonstrasikan cara mengambil data tabel dari website
dengan struktur yang mirip dengan website perizinan pemerintah.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
from datetime import datetime

class PerizinanScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def fetch_page_with_retry(self, url, max_retries=3, delay=2):
        """
        Mengambil halaman dengan retry mechanism
        """
        for attempt in range(max_retries):
            try:
                # Random delay
                time.sleep(random.uniform(delay, delay + 1))
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                print(f"✓ Berhasil mengambil: {url}")
                return response
                
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == max_retries - 1:
                    print(f"✗ Gagal mengambil {url} setelah {max_retries} percobaan")
                    return None
                time.sleep(delay * 2)  # Wait longer before retry
        
        return None
    
    def extract_table_data(self, soup, table_selector=None):
        """
        Ekstrak data dari tabel dengan selector yang fleksibel
        """
        tables_data = []
        
        if table_selector:
            tables = soup.select(table_selector)
        else:
            tables = soup.find_all('table')
        
        for table_idx, table in enumerate(tables):
            table_data = {
                'headers': [],
                'rows': [],
                'table_index': table_idx
            }
            
            # Extract headers
            header_row = table.find('tr')
            if header_row:
                headers = header_row.find_all(['th', 'td'])
                table_data['headers'] = [header.get_text(strip=True) for header in headers]
            
            # Extract all rows
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                
                if any(row_data):  # Only add non-empty rows
                    table_data['rows'].append(row_data)
            
            if table_data['rows']:  # Only add tables with data
                tables_data.append(table_data)
        
        return tables_data
    
    def scrape_wikipedia_table_demo(self):
        """
        Contoh scraping tabel dari Wikipedia
        Mengambil data daftar negara dari Wikipedia sebagai contoh
        """
        url = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
        response = self.fetch_page_with_retry(url)
        
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Cari tabel dengan class wikitable
        table = soup.find('table', class_='wikitable')
        
        if not table:
            print("Tabel tidak ditemukan")
            return None
        
        countries_data = []
        rows = table.find_all('tr')[1:]  # Skip header
        
        for row in rows[:20]:  # Ambil 20 data pertama saja
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:
                rank = cells[0].get_text(strip=True)
                country = cells[1].get_text(strip=True)
                population = cells[2].get_text(strip=True)
                
                countries_data.append({
                    'rank': rank,
                    'country': country,
                    'population': population
                })
        
        return countries_data
    
    def scrape_httpbin_demo(self):
        """
        Contoh menggunakan httpbin.org untuk testing
        """
        url = "http://httpbin.org/html"
        response = self.fetch_page_with_retry(url)
        
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic information
        title = soup.find('title').get_text(strip=True) if soup.find('title') else 'N/A'
        h1_text = soup.find('h1').get_text(strip=True) if soup.find('h1') else 'N/A'
        
        # Find all paragraphs
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
        
        return {
            'title': title,
            'heading': h1_text,
            'paragraphs': paragraphs,
            'paragraph_count': len(paragraphs)
        }
    
    def create_sample_perizinan_data(self):
        """
        Membuat contoh data perizinan untuk demonstrasi
        ketika tidak ada akses ke website perizinan yang sebenarnya
        """
        sample_data = [
            {
                'no_izin': 'IZN001/2024',
                'nama_perusahaan': 'PT. Contoh Industri',
                'jenis_izin': 'Izin Usaha Industri',
                'tanggal_terbit': '2024-01-15',
                'status': 'Aktif',
                'lokasi': 'Jakarta Selatan'
            },
            {
                'no_izin': 'IZN002/2024',
                'nama_perusahaan': 'CV. Sampel Manufacturing',
                'jenis_izin': 'Izin Lingkungan',
                'tanggal_terbit': '2024-02-20',
                'status': 'Aktif',
                'lokasi': 'Bekasi'
            },
            {
                'no_izin': 'IZN003/2024',
                'nama_perusahaan': 'PT. Demo Ekspor',
                'jenis_izin': 'Izin Usaha Perdagangan',
                'tanggal_terbit': '2024-03-10',
                'status': 'Dalam Review',
                'lokasi': 'Tangerang'
            }
        ]
        
        return sample_data
    
    def save_data_multiple_formats(self, data, base_filename):
        """
        Simpan data dalam berbagai format (CSV, Excel, JSON)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = []
        
        try:
            df = pd.DataFrame(data)
            
            # Save as CSV
            csv_path = os.path.join(output_dir, f"{base_filename}_{timestamp}.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            saved_files.append(csv_path)
            print(f"✓ Data disimpan ke CSV: {csv_path}")
            
            # Save as Excel
            excel_path = os.path.join(output_dir, f"{base_filename}_{timestamp}.xlsx")
            df.to_excel(excel_path, index=False, engine='openpyxl')
            saved_files.append(excel_path)
            print(f"✓ Data disimpan ke Excel: {excel_path}")
            
            # Save as JSON
            json_path = os.path.join(output_dir, f"{base_filename}_{timestamp}.json")
            df.to_json(json_path, orient='records', indent=2, force_ascii=False)
            saved_files.append(json_path)
            print(f"✓ Data disimpan ke JSON: {json_path}")
            
        except Exception as e:
            print(f"✗ Error menyimpan data: {e}")
        
        return saved_files
    
    def analyze_webpage_structure(self, url):
        """
        Analisis struktur halaman web untuk membantu identifikasi elemen
        """
        response = self.fetch_page_with_retry(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        analysis = {
            'title': soup.find('title').get_text(strip=True) if soup.find('title') else 'N/A',
            'tables_count': len(soup.find_all('table')),
            'forms_count': len(soup.find_all('form')),
            'links_count': len(soup.find_all('a')),
            'images_count': len(soup.find_all('img')),
            'table_classes': [table.get('class', []) for table in soup.find_all('table')],
            'form_actions': [form.get('action', '') for form in soup.find_all('form')]
        }
        
        return analysis

def main():
    """
    Fungsi utama untuk demonstrasi
    """
    print("=== Demonstrasi Web Scraping untuk Data Perizinan ===")
    print("Menggunakan Python, requests, dan BeautifulSoup\n")
    
    scraper = PerizinanScraper()
    
    # Demo 1: Scraping tabel dari Wikipedia
    print("1. Demo: Scraping tabel negara dari Wikipedia...")
    countries_data = scraper.scrape_wikipedia_table_demo()
    
    if countries_data:
        print(f"✓ Berhasil mengambil {len(countries_data)} data negara")
        scraper.save_data_multiple_formats(countries_data, 'countries_population')
        
        print("\nContoh data:")
        for i, country in enumerate(countries_data[:3], 1):
            print(f"{i}. {country['country']} - Population: {country['population']}")
    
    print("\n" + "="*60 + "\n")
    
    # Demo 2: Testing dengan httpbin
    print("2. Demo: Testing HTML parsing dengan httpbin...")
    html_data = scraper.scrape_httpbin_demo()
    
    if html_data:
        print(f"✓ Berhasil mengambil data HTML")
        print(f"   Title: {html_data['title']}")
        print(f"   Heading: {html_data['heading']}")
        print(f"   Paragraphs: {html_data['paragraph_count']}")
    
    print("\n" + "="*60 + "\n")
    
    # Demo 3: Sample data perizinan
    print("3. Demo: Contoh struktur data perizinan...")
    sample_data = scraper.create_sample_perizinan_data()
    scraper.save_data_multiple_formats(sample_data, 'sample_perizinan')
    
    print(f"✓ Berhasil membuat {len(sample_data)} contoh data perizinan")
    print("\nContoh data perizinan:")
    for i, izin in enumerate(sample_data, 1):
        print(f"{i}. {izin['nama_perusahaan']} - {izin['jenis_izin']} ({izin['status']})")
    
    print("\n=== Petunjuk Penggunaan ===")
    print("1. Untuk website perizinan yang sebenarnya, Anda perlu:")
    print("   - Menganalisis struktur HTML halaman target")
    print("   - Mengidentifikasi selector CSS atau XPath untuk tabel data")
    print("   - Menangani pagination jika data tersebar di beberapa halaman")
    print("   - Menambahkan handling untuk form login jika diperlukan")
    print("2. Selalu periksa robots.txt dan terms of service website")
    print("3. Gunakan delay yang wajar untuk menghindari overload server")
    print("4. Cek folder 'output' untuk melihat hasil scraping")
    
    print("\n=== Selesai ===")

if __name__ == "__main__":
    main()
