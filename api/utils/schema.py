"""
Permit data schema and normalization helpers.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
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

	def to_dict(self) -> Dict[str, Any]:
		return asdict(self)


def ensure_permit_schema(record: Dict[str, Any]) -> Dict[str, Any]:
	"""Map a loose record to our standard Permit fields with sensible defaults."""
	if not isinstance(record, dict):
		return Permit().to_dict()

	def pick(keys):
		for k in keys:
			if k in record and record[k] not in (None, ""):
				return record[k]
		return None

	mapped = Permit(
		nama_perusahaan=pick(["nama_perusahaan", "perusahaan", "nama", "pemohon", "company_name"]),
		alamat=pick(["alamat", "address", "lokasi"]),
		jenis_layanan=pick(["jenis_layanan", "layanan", "service_type", "jenis"]),
		nomor_sk=pick(["nomor_sk", "no_sk", "sk_number", "nomor"]),
		tanggal_berlaku=pick(["tanggal_berlaku", "berlaku", "valid_date", "tanggal"]),
		judul_kegiatan=pick(["judul_kegiatan", "kegiatan", "activity", "judul"]),
		status=pick(["status", "keaktifan"]))

	return mapped.to_dict()
