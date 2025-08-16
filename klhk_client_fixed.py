"""
Client untuk mengakses API PTSP MENLHK
Menganalisis dan mengakses data perizinan dari API resmi
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import urllib.parse
import re
from bs4 import BeautifulSoup

class KLHKClient:
    def __init__(self):
        self.base_url = "https://ptsp.menlhk.go.id/api/front/Public"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://ptsp.menlhk.go.id/',
            'Origin': 'https://ptsp.menlhk.go.id'
        })
        
    def get_status_sk(self, plain: bool = False) -> Optional[Any]:
        """
        Mengambil data status SK dari API KLHK
        """
        try:
            url = f"{self.base_url}/StatusSK"
            params = {'plain': str(plain).lower()}
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return response.text
            else:
                print(f"Error getting StatusSK: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error accessing StatusSK: {e}")
            return None
    
    def search_permits_by_company(self, company_name: str, data: List[Dict]) -> List[Dict]:
        """
        Mencari izin berdasarkan nama perusahaan
        """
        if not data or not isinstance(data, list):
            return []
        
        results = []
        company_name_lower = company_name.lower()
        
        for record in data:
            if isinstance(record, dict):
                # Cari di berbagai field yang mungkin berisi nama perusahaan
                company_fields = ['nama_perusahaan', 'perusahaan', 'nama', 'pemohon', 'company_name']
                
                for field in company_fields:
                    if field in record:
                        field_value = str(record[field]).lower()
                        if company_name_lower in field_value:
                            results.append(record)
                            break
        
        return results
    
    def filter_active_permits(self, data: List[Dict]) -> List[Dict]:
        """
        Filter izin yang masih aktif
        """
        if not data or not isinstance(data, list):
            return []
        
        active_permits = []
        current_date = datetime.now()
        
        for record in data:
            if isinstance(record, dict):
                # Cek berbagai field yang mungkin menunjukkan status atau tanggal berlaku
                status_fields = ['status', 'berlaku', 'tanggal_berlaku', 'expired_date']
                is_active = True
                
                for field in status_fields:
                    if field in record:
                        field_value = str(record[field]).lower()
                        if 'expired' in field_value or 'tidak aktif' in field_value or 'dibatalkan' in field_value:
                            is_active = False
                            break
                
                if is_active:
                    active_permits.append(record)
        
        return active_permits
    
    def format_permit_data(self, data: List[Dict]) -> List[Dict]:
        """
        Format data perizinan untuk response yang lebih clean
        """
        if not data or not isinstance(data, list):
            return []
        
        formatted_data = []
        
        for record in data:
            if isinstance(record, dict):
                # Standarisasi field names
                formatted_record = {}
                
                # Mapping field yang umum
                field_mapping = {
                    'nama_perusahaan': ['nama_perusahaan', 'perusahaan', 'nama', 'pemohon', 'company_name'],
                    'alamat': ['alamat', 'address', 'lokasi'],
                    'jenis_layanan': ['jenis_layanan', 'layanan', 'service_type', 'jenis'],
                    'nomor_sk': ['nomor_sk', 'no_sk', 'sk_number', 'nomor'],
                    'tanggal_berlaku': ['tanggal_berlaku', 'berlaku', 'valid_date', 'tanggal'],
                    'judul_kegiatan': ['judul_kegiatan', 'kegiatan', 'activity', 'judul']
                }
                
                for standard_field, possible_fields in field_mapping.items():
                    for field in possible_fields:
                        if field in record:
                            formatted_record[standard_field] = record[field]
                            break
                    
                    # Jika tidak ditemukan, set sebagai None
                    if standard_field not in formatted_record:
                        formatted_record[standard_field] = None
                
                # Tambahkan metadata
                formatted_record['retrieved_at'] = datetime.now().isoformat()
                formatted_record['source'] = 'PTSP MENLHK'
                
                formatted_data.append(formatted_record)
        
        return formatted_data
    
    def create_sample_data(self) -> List[Dict]:
        """
        Create sample permit data for demonstration when API is not accessible
        """
        sample_data = [
            {
                'nama_perusahaan': 'PT. Semen Indonesia (Persero) Tbk',
                'alamat': 'Jl. Veteran No. 9, Gresik, Jawa Timur',
                'jenis_layanan': 'Izin Lingkungan',
                'nomor_sk': 'SK.123/KLHK/2024',
                'tanggal_berlaku': '2024-01-15',
                'judul_kegiatan': 'Operasional Pabrik Semen',
                'status': 'Aktif'
            },
            {
                'nama_perusahaan': 'PT. Pertamina (Persero)',
                'alamat': 'Jl. Medan Merdeka Timur No. 6, Jakarta Pusat',
                'jenis_layanan': 'Izin Pembuangan Limbah',
                'nomor_sk': 'SK.456/KLHK/2024',
                'tanggal_berlaku': '2024-02-20',
                'judul_kegiatan': 'Pengolahan Minyak Bumi',
                'status': 'Aktif'
            },
            {
                'nama_perusahaan': 'PT. Freeport Indonesia',
                'alamat': 'Jl. TB Simatupang, Jakarta Selatan',
                'jenis_layanan': 'Izin AMDAL',
                'nomor_sk': 'SK.789/KLHK/2024',
                'tanggal_berlaku': '2024-03-10',
                'judul_kegiatan': 'Penambangan Tembaga dan Emas',
                'status': 'Dalam Review'
            },
            {
                'nama_perusahaan': 'CV. Teknologi Hijau Nusantara',
                'alamat': 'Jl. Gatot Subroto, Bandung, Jawa Barat',
                'jenis_layanan': 'Izin Usaha Daur Ulang',
                'nomor_sk': 'SK.101/KLHK/2024',
                'tanggal_berlaku': '2024-04-05',
                'judul_kegiatan': 'Pengolahan Sampah Plastik',
                'status': 'Aktif'
            },
            {
                'nama_perusahaan': 'PT. Indonesia Power',
                'alamat': 'Jl. Jend. Gatot Subroto, Jakarta',
                'jenis_layanan': 'Izin Emisi',
                'nomor_sk': 'SK.202/KLHK/2024',
                'tanggal_berlaku': '2024-05-12',
                'judul_kegiatan': 'Pembangkit Listrik Tenaga Uap',
                'status': 'Aktif'
            }
        ]
        
        return sample_data

def main():
    """
    Test client KLHK
    """
    print("=== Testing KLHK API Client ===\n")
    
    client = KLHKClient()
    
    # Create and use sample data for demonstration
    print("Creating sample data for demonstration...")
    sample_data = client.create_sample_data()
    
    # Format data
    formatted_data = client.format_permit_data(sample_data)
    
    print(f"✓ Created {len(formatted_data)} sample records")
    
    # Tampilkan sample data
    print("\nSample formatted data:")
    if formatted_data:
        sample = formatted_data[0]
        for key, value in sample.items():
            print(f"  {key}: {value}")
    
    print("\n" + "="*50 + "\n")
    
    # Test pencarian
    print("Testing search functionality...")
    test_queries = ["PT", "CV", "INDONESIA"]
    
    for query in test_queries:
        results = client.search_permits_by_company(query, formatted_data)
        print(f"Search '{query}': {len(results)} results")
    
    # Filter active permits
    active_permits = client.filter_active_permits(formatted_data)
    print(f"\nActive permits: {len(active_permits)} out of {len(formatted_data)}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
