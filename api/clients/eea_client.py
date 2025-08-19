from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional
import io
import requests
import pandas as pd
from functools import lru_cache

from api.utils.mappings import normalize_country_name

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

    def get_country_renewables(self, country: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Mengambil data energi terbarukan untuk negara tertentu.
        """
        if not country:
            return None
        
        all_countries = self.get_countries_renewables()
        normalized_country = normalize_country_name(country)
        
        for record in all_countries:
            if normalize_country_name(record.get("country", "")) == normalized_country:
                return record
        return None

    def get_industrial_pollution(self) -> List[Dict[str, Any]]:
        """
        Mengambil dan menormalkan data tren polusi industri.
        """
        # ID ini harus diverifikasi dari API, ini adalah contoh
        dataset_id = "industrial-releases-of-pollutants-to-water"
        raw_data = self._get_parquet_data(dataset_id)
        
        normalized_data = []
        for record in raw_data:
            year = record.get("year")
            if not year:
                continue
                
            def to_float(v):
                try:
                    return float(v) if v not in (None, "") else None
                except Exception:
                    return None
                    
            normalized_data.append({
                "year": int(year),
                "cd_hg_ni_pb": to_float(record.get("cd_hg_ni_pb")),
                "toc": to_float(record.get("toc")),
                "total_n": to_float(record.get("total_n")),
                "total_p": to_float(record.get("total_p")),
                "gva": to_float(record.get("gva")),
            })
        
        # Sort by year
        normalized_data.sort(key=lambda x: x.get("year", 0))
        return normalized_data

    def compute_pollution_trend(self, records: List[Dict[str, Any]], window: int = 3) -> Dict[str, Any]:
        """
        Menghitung tren sederhana berdasarkan data polusi.
        """
        def slope_for(key: str) -> Dict[str, Any]:
            vals = [r.get(key) for r in records if isinstance(r.get(key), (int, float))]
            if len(vals) < 2:
                return {"slope": 0.0, "increase": False}
            sel = vals[-window:] if len(vals) >= window else vals
            s = float(sel[-1] - sel[0])
            return {"slope": s, "increase": s > 0.0}
            
        return {
            "total_n": slope_for("total_n"),
            "total_p": slope_for("total_p")
        }

    def get_indicator(self, *, indicator: Optional[str] = "GHG", country: Optional[str] = None, 
                     year: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Generic indicator method for backward compatibility.
        Handles different types of indicators by routing to appropriate methods.
        """
        try:
            if not indicator:
                indicator = "GHG"
                
            indicator_lower = indicator.lower()
            
            # Route renewable energy indicators
            if "renewable" in indicator_lower or indicator_lower in ["res", "share_res"]:
                if country:
                    result = self.get_country_renewables(country)
                    return [result] if result else []
                else:
                    results = self.get_countries_renewables()
                    return results[:limit] if results else []
            
            # Route GHG/pollution indicators  
            elif indicator_lower in ["ghg", "greenhouse", "pollution", "emissions"]:
                results = self.get_industrial_pollution()
                
                # Apply country filter if specified
                if country:
                    normalized_country = normalize_country_name(country)
                    results = [r for r in results 
                             if normalize_country_name(r.get('country', '')) == normalized_country or
                                normalize_country_name(r.get('countryName', '')) == normalized_country]
                
                # Apply year filter if specified  
                if year:
                    results = [r for r in results 
                             if r.get('year') == year or r.get('reportingYear') == year]
                
                return results[:limit] if results else []
            
            # Default fallback - return renewable energy data
            else:
                logger.warning(f"Unknown indicator '{indicator}', defaulting to renewable energy")
                if country:
                    result = self.get_country_renewables(country)
                    return [result] if result else []
                else:
                    results = self.get_countries_renewables()
                    return results[:limit] if results else []
                    
        except Exception as e:
            logger.error(f"Error in get_indicator: {e}")
            return []

__all__ = ["EEAClient"]