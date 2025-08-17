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


@dataclass
class ISOCert:
	company: Optional[str] = None
	country: Optional[str] = None
	certificate: Optional[str] = None
	valid_until: Optional[str] = None
	source: str = "ISO"
	retrieved_at: str = datetime.now().isoformat()
	raw: Dict[str, Any] = field(default_factory=dict)

	def to_dict(self) -> Dict[str, Any]:
		return asdict(self)


@dataclass
class EEAEnv:
	country: Optional[str] = None
	indicator: Optional[str] = None
	year: Optional[int] = None
	value: Optional[float] = None
	unit: Optional[str] = None
	source: str = "EEA"
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

	company = _pick(["facility_name", "plant_name", "company_name", "nama_perusahaan", "facility"])
	state = record.get("state") or record.get("state_name") or record.get("state_abbr")
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
			"plant_id": record.get("plant_id") or record.get("facility_id") or record.get("tri_facility_id") or record.get("registry_id"),
			"emissions": record.get("emissions"),
			"unit": record.get("unit"),
			"state": state,
			"county": county,
			"raw": {k: v for k, v in record.items() if k not in {"facility_name", "plant_name", "company_name", "state", "county", "year", "pollutant", "emissions", "unit", "plant_id", "facility_id"}},
		},
	)

	return mapped.to_dict()


def ensure_iso_cert_schema(record: Dict[str, Any]) -> Dict[str, Any]:
	if not isinstance(record, dict):
		return ISOCert().to_dict()
	company = record.get("company") or record.get("organization")
	country = record.get("country")
	certificate = record.get("certificate") or record.get("standard")
	valid_until = record.get("valid_until") or record.get("expiry")
	mapped = ISOCert(
		company=company,
		country=country,
		certificate=certificate,
		valid_until=valid_until,
		raw={k: v for k, v in record.items() if k not in {"company", "organization", "country", "certificate", "standard", "valid_until", "expiry"}},
	)
	# also provide Permit-like view
	permit_like = Permit(
		nama_perusahaan=company,
		alamat=None,
		jenis_layanan="ISO Certification",
		nomor_sk=None,
		tanggal_berlaku=valid_until,
		judul_kegiatan=certificate,
		status=None,
		source="ISO",
		extras={"country": country, "raw": mapped.raw},
	)
	return permit_like.to_dict()


def ensure_eea_env_schema(record: Dict[str, Any]) -> Dict[str, Any]:
	if not isinstance(record, dict):
		return EEAEnv().to_dict()
	country = record.get("country")
	indicator = record.get("indicator")
	year = record.get("year")
	value = record.get("value")
	unit = record.get("unit")
	mapped = EEAEnv(
		country=country,
		indicator=indicator,
		year=int(year) if year is not None else None,
		value=float(value) if value is not None else None,
		unit=unit,
		raw={k: v for k, v in record.items() if k not in {"country", "indicator", "year", "value", "unit"}},
	)
	# Permit-like normalized output
	permit_like = Permit(
		nama_perusahaan=None,
		alamat=country,
		jenis_layanan="EEA Indicator",
		nomor_sk=None,
		tanggal_berlaku=str(mapped.year) if mapped.year is not None else None,
		judul_kegiatan=indicator,
		status=None,
		source="EEA",
		extras={"value": mapped.value, "unit": mapped.unit, "raw": mapped.raw},
	)
	return permit_like.to_dict()
