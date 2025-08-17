"""
Permit data schema and normalization helpers.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Permit:
	nama_perusahaan: Optional[str] = None
	alamat: Optional[str] = None
	jenis_layanan: Optional[str] = None
	nomor_sk: Optional[str] = None
	tanggal_berlaku: Optional[str] = None
	judul_kegiatan: Optional[str] = None
	status: Optional[str] = None
	source: str = "PTSP MENLHK"
	retrieved_at: str = datetime.now().isoformat()
	extras: Dict[str, Any] = field(default_factory=dict)

	def to_dict(self) -> Dict[str, Any]:
		return asdict(self)


@dataclass
class EPAEmission:
	"""Schema for raw EPA emission data normalized shape (subset)."""
	facility_name: Optional[str] = None
	plant_id: Optional[str] = None
	state: Optional[str] = None
	county: Optional[str] = None
	year: Optional[int] = None
	pollutant: Optional[str] = None
	emissions: Optional[float] = None
	unit: Optional[str] = None
	source: str = "EPA Envirofacts"
	retrieved_at: str = datetime.now().isoformat()
	raw: Dict[str, Any] = field(default_factory=dict)

	def to_dict(self) -> Dict[str, Any]:
		return asdict(self)


def ensure_permit_schema(record: Dict[str, Any]) -> Dict[str, Any]:
	"""Map a loose record to our standard Permit fields with sensible defaults."""
	if not isinstance(record, dict):
		return Permit().to_dict()

	def _pick(keys):
		for k in keys:
			if k in record and record[k] not in (None, ""):
				return record[k]
		return None

	mapped = Permit(
		nama_perusahaan=_pick(["nama_perusahaan", "perusahaan", "nama", "pemohon", "company_name"]),
		alamat=_pick(["alamat", "address", "lokasi"]),
		jenis_layanan=_pick(["jenis_layanan", "layanan", "service_type", "jenis"]),
		nomor_sk=_pick(["nomor_sk", "no_sk", "sk_number", "nomor"]),
		tanggal_berlaku=_pick(["tanggal_berlaku", "berlaku", "valid_date", "tanggal"]),
		judul_kegiatan=_pick(["judul_kegiatan", "kegiatan", "activity", "judul"]),
		status=_pick(["status", "keaktifan"]))

	return mapped.to_dict()


def ensure_epa_emission_schema(record: Dict[str, Any]) -> Dict[str, Any]:
	"""Normalize EPA emissions record to the Permit schema + extras."""
	if not isinstance(record, dict):
		return Permit().to_dict()

	def _pick(keys):
		for k in keys:
			if k in record and record[k] not in (None, ""):
				return record[k]
		return None

	company = _pick(["facility_name", "plant_name", "company_name", "nama_perusahaan"])
	state = record.get("state") or record.get("state_name")
	county = record.get("county") or record.get("county_name")
	addr_parts = [str(x) for x in [county, state] if x]
	alamat = ", ".join(addr_parts) if addr_parts else None

	mapped = Permit(
		nama_perusahaan=company,
		alamat=alamat,
		jenis_layanan="EPA Emission Data",
		nomor_sk=None,
		tanggal_berlaku=str(record.get("year")) if record.get("year") is not None else None,
		judul_kegiatan=str(record.get("pollutant")) if record.get("pollutant") is not None else None,
		status=None,
		source="EPA Envirofacts",
		extras={
			"plant_id": record.get("plant_id") or record.get("facility_id"),
			"emissions": record.get("emissions"),
			"unit": record.get("unit"),
			"state": state,
			"county": county,
			"raw": {k: v for k, v in record.items() if k not in {"facility_name", "plant_name", "company_name", "state", "county", "year", "pollutant", "emissions", "unit", "plant_id", "facility_id"}},
		},
	)

	return mapped.to_dict()
