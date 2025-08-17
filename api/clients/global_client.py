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
		# Envirofacts efservice base (documented)
		# Format: https://data.epa.gov/efservice/<Table>/<Column>/<Operator>/<Value>/rows/0:n/JSON
		self.env_base = os.getenv("EPA_ENV_BASE", "https://data.epa.gov/efservice/").rstrip("/") + "/"
		# Default table: use TRI facility for a stable, public dataset
		# You can override with EPA_ENV_TABLE (e.g., tri_facility, tri_release)
		self.env_table = os.getenv("EPA_ENV_TABLE", "tri_facility").strip("/")
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
		timeout: Optional[float] = None,
	) -> List[Dict[str, Any]]:
		"""
		Ambil data fasilitas (sebagai proxy emisi) dari Envirofacts efservice.
		Menggunakan format URL terdokumentasi: data.epa.gov/efservice
		- Default tabel: tri_facility (stabil dan publik)
		- Filter yang dipakai: state_abbr (jika diberikan)
		- Pembatasan baris: rows/0:(limit-1)
		Catatan: Untuk dataset lain, set EPA_ENV_TABLE; sesuaikan kolom filter.
		Jika permintaan gagal, kembalikan sample data.
		"""
		# Bangun path sesuai format efservice
		segments: List[str] = [self.env_table]
		if state:
			segments.extend(["state_abbr", state])
		# TRI facility tidak menyediakan kolom 'year' langsung; abaikan jika diberikan
		# Pembatasan baris (0-indexed, inclusive)
		end_row = max(0, (limit or 100) - 1)
		segments.extend(["rows", f"0:{end_row}", "JSON"])

		url = f"{self.env_base}{'/'.join(segments)}"

		try:
			req_timeout = timeout if (timeout is not None and timeout > 0) else 30
			resp = self.session.get(url, timeout=req_timeout)
			if resp.status_code == 200:
				data = resp.json()
				if not isinstance(data, list):
					raise ValueError("Unexpected EPA response shape (expected list)")
				return data
			else:
				logger.warning(f"EPA Envirofacts HTTP {resp.status_code} for {url}, using sample data")
				return self.create_sample_data()
		except Exception as e:
			logger.error(f"Error fetching EPA data from {url}: {e}")
			return self.create_sample_data()


# Export with legacy name for compatibility
KLHKClient = EPAClient

__all__ = ["KLHKClient", "EPAClient"]
