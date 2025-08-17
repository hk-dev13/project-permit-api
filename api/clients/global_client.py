"""
EPA Global Client

Implementasi klien untuk mengambil data emisi pembangkit listrik dari EPA.
Tetap mengekspor nama kelas sebagai `KLHKClient` untuk kompatibilitas
dengan bagian lain aplikasi yang sudah mengimpor nama tersebut.
"""

from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional

import requests

from api.utils.schema import ensure_epa_emission_schema

logger = logging.getLogger(__name__)


class EPAClient:
	"""
	Klien EPA untuk mengambil data emisi pembangkit listrik.

	Sumber default: Envirofacts efservice (konfig via env var)
	Fallback opsional: EASEY/CAMD (dapat ditambahkan kemudian)
	"""

	def __init__(self) -> None:
		# Envirofacts base endpoint (OData-like)
		# Contoh: https://enviro.epa.gov/enviro/efservice/
		self.env_base = os.getenv("EPA_ENV_BASE", "https://enviro.epa.gov/enviro/efservice/").rstrip("/") + "/"
		# Resource/table default (disesuaikan jika berbeda)
		# Catatan: Nama resource Envirofacts bervariasi per dataset (e.g., egrid, ghgrp, dll)
		# Anda dapat men-set EPA_ENV_RESOURCE melalui environment variable.
		self.env_resource = os.getenv("EPA_ENV_RESOURCE", "egrid/PLANT/JSON")
		self.session = requests.Session()
		self.session.headers.update({
			"Accept": "application/json",
			"User-Agent": "project-permit-api/1.0 (+https://github.com/hk-dev13)"
		})

	# --- Public API expected by routes ---
	def get_status_sk(self, plain: bool = False) -> Optional[List[Dict[str, Any]]]:
		"""
		Untuk kompatibilitas: kembalikan daftar record data emisi.
		Parameter `plain` diabaikan.
		"""
		try:
			records = self.get_emissions_power_plants(limit=200)
			return records
		except Exception as e:
			logger.error(f"EPAClient.get_status_sk error: {e}")
			return None

	def search_permits_by_company(self, company_name: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		"""Cari berdasarkan nama fasilitas/pabrik (facility/plant name)."""
		if not data:
			return []
		key_candidates = ["nama_perusahaan", "facility_name", "plant_name", "facility", "company_name"]
		term = company_name.lower()
		results: List[Dict[str, Any]] = []
		for rec in data:
			for k in key_candidates:
				val = str(rec.get(k, "") or "").lower()
				if term in val:
					results.append(rec)
					break
		return results

	def filter_active_permits(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		"""
		Data emisi tidak memiliki konsep 'aktif' seperti izin.
		Untuk kompatibilitas, kembalikan data apa adanya.
		"""
		return list(data or [])

	def format_permit_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		"""Normalisasi record EPA ke skema standar Permit + extras (EPA)."""
		if not data:
			return []
		return [ensure_epa_emission_schema(rec) for rec in data if isinstance(rec, dict)]

	def create_sample_data(self) -> List[Dict[str, Any]]:
		"""
		Data sample emisi EPA untuk fallback/demonstrasi.
		"""
		return [
			{
				"facility_name": "Sample Coal Plant A",
				"plant_id": "PLT1001",
				"state": "TX",
				"county": "Harris",
				"year": 2023,
				"pollutant": "CO2",
				"emissions": 1234567.89,
				"unit": "tons"
			},
			{
				"facility_name": "Sample Gas Plant B",
				"plant_id": "PLT2002",
				"state": "CA",
				"county": "Los Angeles",
				"year": 2023,
				"pollutant": "CO2",
				"emissions": 234567.0,
				"unit": "tons"
			}
		]

	# --- EPA-specific helpers ---
	def get_emissions_power_plants(
		self,
		*,
		state: Optional[str] = None,
		year: Optional[int] = None,
		limit: int = 100,
	) -> List[Dict[str, Any]]:
		"""
		Ambil data emisi pembangkit listrik dari Envirofacts (jika tersedia).
		Catatan: Struktur resource Envirofacts bervariasi; endpoint default dapat disesuaikan via env var.
		Jika permintaan gagal, kembalikan sample data.
		"""
		url = f"{self.env_base}{self.env_resource}"

		params: Dict[str, Any] = {}
		# Beberapa resource Envirofacts menggunakan segment path untuk filter, bukan query params.
		# Di sini kita tetap kirim params standar; jika server mengabaikan, tidak berdampak.
		if state:
			params["state"] = state
		if year:
			params["year"] = year

		try:
			resp = self.session.get(url, params=params, timeout=30)
			if resp.status_code == 200:
				data = resp.json()
				# Pastikan list
				if isinstance(data, dict):
					# beberapa layanan bisa mengembalikan objek dengan key data
					data = data.get("data", [])  # type: ignore[assignment]
				if not isinstance(data, list):
					raise ValueError("Unexpected EPA response shape")
				# Optional trimming
				if limit and len(data) > limit:
					data = data[:limit]
				return data
			else:
				logger.warning(f"EPA Envirofacts HTTP {resp.status_code}, using sample data")
				return self.create_sample_data()
		except Exception as e:
			logger.error(f"Error fetching EPA data: {e}")
			return self.create_sample_data()


# Export with legacy name for compatibility
KLHKClient = EPAClient

__all__ = ["KLHKClient", "EPAClient"]
