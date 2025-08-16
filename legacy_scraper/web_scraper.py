"""
Web Scraping Script - Demonstrasi Dasar
Menggunakan requests dan BeautifulSoup untuk mengambil data dari website
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urljoin, urlparse
import os

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        # Set user agent agar tidak terblokir
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_page(self, url, delay=1):
        """
        Mengambil halaman web dengan delay untuk menghindari rate limiting
        """
        try:
            # Random delay untuk menghindari deteksi bot
            time.sleep(random.uniform(delay, delay + 1))
            
            response = self.session.get(url)
            response.raise_for_status()  # Raise exception untuk HTTP errors
            
            print(f"✓ Berhasil mengambil: {url}")
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error mengambil {url}: {e}")
            return None
    
    def parse_html(self, html_content):
        """
        Parse HTML menggunakan BeautifulSoup
        """
        return BeautifulSoup(html_content, 'html.parser')
    
    def extract_links(self, soup, base_url):
        """
        Ekstrak semua link dari halaman
        """
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            text = link.get_text(strip=True)
            
            links.append({
                'url': full_url,
                'text': text,
                'href': href
            })
        
        return links
    
    def extract_tables(self, soup):
        """
        Ekstrak semua tabel dari halaman
        """
        tables_data = []
        tables = soup.find_all('table')
        
        for i, table in enumerate(tables):
            table_data = []
            rows = table.find_all('tr')
            
            for row in rows:
                row_data = []
                cells = row.find_all(['td', 'th'])
                
                for cell in cells:
                    row_data.append(cell.get_text(strip=True))
                
                if row_data:  # Hanya tambahkan jika ada data
                    table_data.append(row_data)
            
            if table_data:
                tables_data.append({
                    'table_index': i,
                    'data': table_data
                })
        
        return tables_data
    
    def extract_text_content(self, soup):
        """
        Ekstrak konten teks utama dari halaman
        """
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def save_to_csv(self, data, filename):
        """
        Simpan data ke file CSV
        """
        try:
            df = pd.DataFrame(data)
            output_path = os.path.join('output', filename)
            
            # Buat folder output jika belum ada
            os.makedirs('output', exist_ok=True)
            
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"✓ Data berhasil disimpan ke: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Error menyimpan data: {e}")
            return None
    
    def scrape_quotes_demo(self):
        """
        Contoh scraping menggunakan website quotes.toscrape.com
        Website ini dibuat khusus untuk latihan web scraping
        """
        base_url = "http://quotes.toscrape.com"
        response = self.fetch_page(base_url)
        
        if not response:
            return None
        
        soup = self.parse_html(response.content)
        
        quotes_data = []
        quotes = soup.find_all('div', class_='quote')
        
        for quote in quotes:
            text = quote.find('span', class_='text').get_text(strip=True)
            author = quote.find('small', class_='author').get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote.find_all('a', class_='tag')]
            
            quotes_data.append({
                'quote': text,
                'author': author,
                'tags': ', '.join(tags)
            })
        
        return quotes_data
    
    def scrape_books_demo(self):
        """
        Contoh scraping books.toscrape.com
        """
        base_url = "http://books.toscrape.com"
        response = self.fetch_page(base_url)
        
        if not response:
            return None
        
        soup = self.parse_html(response.content)
        
        books_data = []
        books = soup.find_all('article', class_='product_pod')
        
        for book in books:
            title_elem = book.find('h3').find('a')
            title = title_elem.get('title', 'N/A')
            
            price_elem = book.find('p', class_='price_color')
            price = price_elem.get_text(strip=True) if price_elem else 'N/A'
            
            rating_elem = book.find('p', class_='star-rating')
            rating = rating_elem.get('class')[1] if rating_elem else 'N/A'
            
            availability_elem = book.find('p', class_='instock availability')
            availability = availability_elem.get_text(strip=True) if availability_elem else 'N/A'
            
            books_data.append({
                'title': title,
                'price': price,
                'rating': rating,
                'availability': availability
            })
        
        return books_data

def main():
    """
    Fungsi utama untuk menjalankan demonstrasi web scraping
    """
    print("=== Web Scraping Demonstration ===")
    print("Menggunakan Python, requests, dan BeautifulSoup\n")
    
    scraper = WebScraper()
    
    # Demo 1: Scraping quotes
    print("1. Scraping quotes dari quotes.toscrape.com...")
    quotes_data = scraper.scrape_quotes_demo()
    
    if quotes_data:
        print(f"✓ Berhasil mengambil {len(quotes_data)} quotes")
        scraper.save_to_csv(quotes_data, 'quotes_data.csv')
        
        # Tampilkan contoh data
        print("\nContoh data yang berhasil diambil:")
        for i, quote in enumerate(quotes_data[:3], 1):
            print(f"{i}. \"{quote['quote'][:50]}...\" - {quote['author']}")
    
    print("\n" + "="*50 + "\n")
    
    # Demo 2: Scraping books
    print("2. Scraping books dari books.toscrape.com...")
    books_data = scraper.scrape_books_demo()
    
    if books_data:
        print(f"✓ Berhasil mengambil {len(books_data)} books")
        scraper.save_to_csv(books_data, 'books_data.csv')
        
        # Tampilkan contoh data
        print("\nContoh data yang berhasil diambil:")
        for i, book in enumerate(books_data[:3], 1):
            print(f"{i}. {book['title']} - {book['price']} ({book['rating']} stars)")
    
    print("\n=== Selesai ===")
    print("Cek folder 'output' untuk melihat file CSV yang dihasilkan.")

if __name__ == "__main__":
    main()
