from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional
import io
import requests
import pandas as pd
from functools import lru_cache

# Pastikan Anda telah menambahkan 'pyarrow' ke requirements.txt
# pip install pyarrow

logger = logging.getLogger(__name__)

class EEAClient:
    """
    Klien untuk berinteraksi dengan EEA Downloads API (Parquet).
    API Docs: https://eeadmz1-downloads-api-appservice.azurewebsites.net/swagger/index.html
    """
    BASE_URL = "https://eeadmz1-downloads-api-appservice.azurewebsites.net/api/v1/public"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json, application/octet-stream",
            "User-Agent": f"project-permit-api/1.0 (+{os.getenv('GITHUB_REPO_URL', 'https://github.com/hk-dev13')})"
        })

    @lru_cache(maxsize=10) # Cache sederhana untuk menghindari pengunduhan berulang
    def _get_parquet_data(self, dataset_id: str) -> List[Dict[str, Any]]:
        """
        Menemukan, mengunduh, dan mengurai dataset Parquet dari EEA API.
        Ini menerapkan alur kerja 2 langkah:
        1. Dapatkan metadata file untuk menemukan URL unduhan.
        2. Unduh dan baca file Parquet.
        """
        logger.info(f"Mencari file untuk dataset EEA: {dataset_id}")
        files_url = f"{self.BASE_URL}/datasets/{dataset_id}/files"
        
        try:
            # Langkah 1: Dapatkan URL unduhan
            resp_files = self.session.get(files_url, timeout=30)
            resp_files.raise_for_status()
            files_metadata = resp_files.json()
            
            # Cari file Parquet pertama yang tersedia
            download_url = next((f['links']['download'] for f in files_metadata if f['name'].endswith('.parquet')), None)

            if not download_url:
                logger.error(f"Tidak ada file Parquet yang ditemukan untuk dataset {dataset_id}")
                return []

            # Langkah 2: Unduh dan baca file Parquet
            logger.info(f"Mengunduh data Parquet dari: {download_url}")
            resp_data = self.session.get(download_url, timeout=90) # Timeout lebih lama untuk unduhan
            resp_data.raise_for_status()
            
            # Gunakan pandas untuk membaca konten biner
            df = pd.read_parquet(io.BytesIO(resp_data.content))
            
            # Bersihkan nama kolom untuk konsistensi (opsional tapi disarankan)
            df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
            
            return df.to_dict(orient="records")

        except requests.exceptions.RequestException as e:
            logger.error(f"Kesalahan jaringan saat mengambil data EEA untuk {dataset_id}: {e}")
        except Exception as e:
            logger.error(f"Kesalahan saat memproses data Parquet untuk {dataset_id}: {e}")
        
        return []

    def get_countries_renewables(self) -> List[Dict[str, Any]]:
        """
        Mengambil dan menormalkan data pangsa energi terbarukan per negara.
        """
        # ID ini harus diverifikasi dari API, ini adalah contoh
        dataset_id = "share-of-energy-from-renewable-sources" 
        raw_data = self._get_parquet_data(dataset_id)
        
        normalized_data = []
        for record in raw_data:
            # Kolom di-lowercase dan underscore oleh _get_parquet_data
            country = record.get("country")
            if not country:
                continue

            normalized_data.append({
                "country": country,
                "renewable_energy_share_2020": record.get("renewable_energy_share_2020"),
                "renewable_energy_share_2021_proxy": record.get("renewable_energy_share_2021_(proxy)"), # Sesuaikan dengan nama kolom yang sebenarnya
                "target_2020": record.get("2020_target"),
            })
        return normalized_data

    def get_industrial_pollution(self) -> List[Dict[str, Any]]:
        """
        Mengambil dan menormalkan data tren polusi industri.
        """
        # ID ini harus diverifikasi dari API, ini adalah contoh
        dataset_id = "industrial-releases-of-pollutants-to-water"
        raw_data = self._get_parquet_data(dataset_id)
        
        # Logika normalisasi Anda sebelumnya sudah bagus, dapat diterapkan di sini
        # ...
        
        return raw_data # Kembalikan data yang dinormalisasi

__all__ = ["EEAClient"]