"""
Advanced Web Scraping - Handling Forms, Sessions, dan Authentication
Script ini mendemonstrasikan teknik scraping yang lebih advanced
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import os
from urllib.parse import urljoin

class AdvancedScraper:
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
    
    def login_to_website(self, login_url, username, password, username_field='username', password_field='password'):
        """
        Template untuk login ke website dengan form
        """
        try:
            # Ambil halaman login untuk mendapatkan CSRF token atau hidden fields
            login_page = self.session.get(login_url)
            soup = BeautifulSoup(login_page.content, 'html.parser')
            
            # Cari form login
            form = soup.find('form')
            if not form:
                print("Form login tidak ditemukan")
                return False
            
            # Ekstrak hidden fields (seperti CSRF token)
            form_data = {}
            for input_field in form.find_all('input'):
                field_name = input_field.get('name')
                field_value = input_field.get('value', '')
                
                if field_name:
                    form_data[field_name] = field_value
            
            # Set username dan password
            form_data[username_field] = username
            form_data[password_field] = password
            
            # Submit form
            form_action = form.get('action', login_url)
            if not form_action.startswith('http'):
                form_action = urljoin(login_url, form_action)
            
            response = self.session.post(form_action, data=form_data)
            
            # Check apakah login berhasil
            if "dashboard" in response.url.lower() or "welcome" in response.text.lower():
                print("✓ Login berhasil")
                return True
            else:
                print("✗ Login gagal")
                return False
                
        except Exception as e:
            print(f"Error saat login: {e}")
            return False
    
    def scrape_with_pagination(self, base_url, max_pages=5):
        """
        Scraping data yang tersebar di multiple halaman
        """
        all_data = []
        current_page = 1
        
        while current_page <= max_pages:
            print(f"Scraping halaman {current_page}...")
            
            # Buat URL untuk halaman tertentu
            if '?' in base_url:
                url = f"{base_url}&page={current_page}"
            else:
                url = f"{base_url}?page={current_page}"
            
            response = self.session.get(url)
            if response.status_code != 200:
                print(f"Error mengambil halaman {current_page}")
                break
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ekstrak data dari halaman ini
            page_data = self.extract_data_from_page(soup)
            
            if not page_data:  # Tidak ada data lagi
                print("Tidak ada data lagi, berhenti scraping")
                break
            
            all_data.extend(page_data)
            
            # Check apakah ada halaman selanjutnya
            next_link = soup.find('a', text='Next') or soup.find('a', class_='next')
            if not next_link:
                print("Tidak ada halaman selanjutnya")
                break
            
            current_page += 1
            time.sleep(2)  # Delay antar halaman
        
        return all_data
    
    def extract_data_from_page(self, soup):
        """
        Ekstrak data dari satu halaman (customize sesuai struktur website)
        """
        data = []
        
        # Contoh: ekstrak dari tabel
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    data.append(row_data)
        
        return data
    
    def handle_ajax_requests(self, base_url, ajax_endpoint, params=None):
        """
        Handling AJAX requests untuk data yang dimuat dinamis
        """
        if params is None:
            params = {}
        
        try:
            # Set headers khusus untuk AJAX
            ajax_headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'Referer': base_url
            }
            
            response = self.session.get(ajax_endpoint, params=params, headers=ajax_headers)
            
            if response.status_code == 200:
                # Coba parse sebagai JSON
                try:
                    data = response.json()
                    print(f"✓ Berhasil mengambil data AJAX: {len(data)} items")
                    return data
                except json.JSONDecodeError:
                    # Fallback ke HTML parsing
                    soup = BeautifulSoup(response.content, 'html.parser')
                    return soup
            else:
                print(f"Error AJAX request: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error handling AJAX: {e}")
            return None
    
    def scrape_with_search_form(self, search_url, search_query):
        """
        Scraping dengan menggunakan form search
        """
        try:
            # Ambil halaman search
            search_page = self.session.get(search_url)
            soup = BeautifulSoup(search_page.content, 'html.parser')
            
            # Cari form search
            search_form = soup.find('form', {'action': lambda x: 'search' in str(x).lower() if x else False}) or soup.find('form')
            
            if not search_form:
                print("Form search tidak ditemukan")
                return None
            
            # Ekstrak form data
            form_data = {}
            for input_field in search_form.find_all('input'):
                field_name = input_field.get('name')
                field_value = input_field.get('value', '')
                
                if field_name:
                    # Cek apakah ini field search
                    if 'search' in field_name.lower() or 'query' in field_name.lower() or 'q' == field_name.lower():
                        form_data[field_name] = search_query
                    else:
                        form_data[field_name] = field_value
            
            # Submit search form
            form_action = search_form.get('action', search_url)
            if not form_action.startswith('http'):
                form_action = urljoin(search_url, form_action)
            
            response = self.session.post(form_action, data=form_data)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self.extract_data_from_page(soup)
            else:
                print(f"Error search: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error scraping dengan search form: {e}")
            return None
    
    def save_cookies(self, filename='cookies.json'):
        """
        Simpan cookies untuk session selanjutnya
        """
        cookies_dict = dict(self.session.cookies)
        with open(filename, 'w') as f:
            json.dump(cookies_dict, f, indent=2)
        print(f"✓ Cookies disimpan ke {filename}")
    
    def load_cookies(self, filename='cookies.json'):
        """
        Load cookies dari file
        """
        try:
            with open(filename, 'r') as f:
                cookies_dict = json.load(f)
            
            for name, value in cookies_dict.items():
                self.session.cookies.set(name, value)
            
            print(f"✓ Cookies dimuat dari {filename}")
            return True
        except FileNotFoundError:
            print(f"File cookies {filename} tidak ditemukan")
            return False
    
    def demo_httpbin_forms(self):
        """
        Demo menggunakan httpbin.org untuk test form submission
        """
        print("Demo: Form submission dengan httpbin...")
        
        # Test POST form
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'This is a test message from web scraper'
        }
        
        response = self.session.post('http://httpbin.org/post', data=form_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Form berhasil disubmit")
            print(f"  Data yang dikirim: {result.get('form', {})}")
            return result
        else:
            print("✗ Form submission gagal")
            return None
    
    def demo_cookies_and_session(self):
        """
        Demo handling cookies dan session
        """
        print("Demo: Cookies dan Session handling...")
        
        # Set some cookies via httpbin
        cookie_url = "http://httpbin.org/cookies/set"
        params = {
            'session_id': '12345',
            'user_pref': 'dark_mode'
        }
        
        response = self.session.get(cookie_url, params=params)
        
        # Check cookies
        cookies_url = "http://httpbin.org/cookies"
        response = self.session.get(cookies_url)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Session dan cookies bekerja")
            print(f"  Cookies: {result.get('cookies', {})}")
            return result
        else:
            print("✗ Session handling gagal")
            return None

def main():
    """
    Demo advanced web scraping techniques
    """
    print("=== Advanced Web Scraping Demonstration ===")
    print("Mendemonstrasikan form handling, sessions, dan teknik advanced\n")
    
    scraper = AdvancedScraper()
    
    # Demo 1: Form submission
    form_result = scraper.demo_httpbin_forms()
    
    print("\n" + "="*60 + "\n")
    
    # Demo 2: Cookies dan Session
    session_result = scraper.demo_cookies_and_session()
    
    print("\n" + "="*60 + "\n")
    
    # Demo 3: Save cookies
    scraper.save_cookies('demo_cookies.json')
    
    print("\n=== Tips untuk Website Perizinan Yang Sebenarnya ===")
    print("1. Login Form Handling:")
    print("   - Analisis form login untuk CSRF token")
    print("   - Simpan session cookies setelah login")
    print("   - Handle redirect setelah login")
    
    print("2. Search Form:")
    print("   - Identifikasi form search dan parameter yang diperlukan")
    print("   - Handle hasil search yang ter-paginate")
    print("   - Extract data dari hasil search")
    
    print("3. Session Management:")
    print("   - Simpan cookies untuk menghindari login berulang")
    print("   - Handle session timeout")
    print("   - Maintain session state across requests")
    
    print("4. Error Handling:")
    print("   - Retry mechanism untuk request yang gagal")
    print("   - Handle rate limiting")
    print("   - Logging untuk debugging")
    
    print("\n=== Selesai ===")

if __name__ == "__main__":
    main()
