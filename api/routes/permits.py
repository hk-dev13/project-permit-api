from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import urllib.parse
import logging

from clients.global_client import KLHKClient
from utils import cache as cache_util
from utils.schema import ensure_permit_schema

permits_bp = Blueprint("permits_bp", __name__)

logger = logging.getLogger(__name__)

def _fetch_and_normalize():
	"""Fetcher used by cache layer to get fresh data and normalize to schema."""
	logger.info("Fetching fresh permit data from KLHK API")
	client = KLHKClient()
	try:
		sk_data = client.get_status_sk(plain=False)
		data = sk_data if (sk_data and isinstance(sk_data, list)) else client.create_sample_data()
	except Exception as e:
		logger.error(f"Error fetching KLHK data: {e}")
		data = client.create_sample_data()

	# Normalize every record to Permit schema
	normalized = [ensure_permit_schema(rec) for rec in data if isinstance(rec, dict)]
	return normalized


def _get_cached_data():
	data = cache_util.get_or_set(_fetch_and_normalize)
	# Update app config timestamp for health
	ts = cache_util.get_cache_timestamp()
	if ts:
		try:
			current_app.config["CACHE_TIMESTAMP"] = ts
		except Exception:
			pass
	return data


@permits_bp.route('/permits', methods=['GET'])
def get_all_permits():
	"""Get all permits with optional pagination."""
	try:
		page = int(request.args.get('page', 1))
		limit = int(request.args.get('limit', 50))

		if page < 1:
			page = 1
		if limit < 1 or limit > 100:
			limit = 50

		data = _get_cached_data()

		start_idx = (page - 1) * limit
		end_idx = start_idx + limit
		paginated_data = data[start_idx:end_idx]

		return jsonify({
			'status': 'success',
			'data': paginated_data,
			'pagination': {
				'page': page,
				'limit': limit,
				'total_records': len(data),
				'total_pages': (len(data) + limit - 1) // limit,
				'has_next': end_idx < len(data),
				'has_prev': page > 1
			},
			'retrieved_at': datetime.now().isoformat()
		})

	except Exception as e:
		logger.error(f"Error in get_all_permits: {e}")
		return jsonify({'status': 'error', 'message': str(e)}), 500


@permits_bp.route('/permits/search', methods=['GET'])
def search_permits():
	"""Search permits by company name or other parameters."""
	try:
		nama = request.args.get('nama', '').strip()
		jenis = request.args.get('jenis', '').strip()
		status = request.args.get('status', '').strip()

		if not any([nama, jenis, status]):
			return jsonify({
				'status': 'error',
				'message': 'At least one search parameter required (nama, jenis, or status)'
			}), 400

		data = _get_cached_data()
		filtered_data = []

		for permit in data:
			match = True

			if nama:
				company_name = permit.get('nama_perusahaan', '') or ''
				if nama.lower() not in company_name.lower():
					match = False

			if jenis and match:
				permit_type = permit.get('jenis_layanan', '') or ''
				if jenis.lower() not in permit_type.lower():
					match = False

			if status and match:
				permit_status = permit.get('status', '') or ''
				if status.lower() not in permit_status.lower():
					match = False

			if match:
				filtered_data.append(permit)

		return jsonify({
			'status': 'success',
			'data': filtered_data,
			'search_params': {
				'nama': nama,
				'jenis': jenis,
				'status': status
			},
			'total_found': len(filtered_data),
			'retrieved_at': datetime.now().isoformat()
		})

	except Exception as e:
		logger.error(f"Error in search_permits: {e}")
		return jsonify({'status': 'error', 'message': str(e)}), 500


@permits_bp.route('/permits/active', methods=['GET'])
def get_active_permits():
	"""Get only active permits."""
	try:
		data = _get_cached_data()

		client = KLHKClient()
		active_permits = client.filter_active_permits(data)

		return jsonify({
			'status': 'success',
			'data': active_permits,
			'total_active': len(active_permits),
			'total_all': len(data),
			'retrieved_at': datetime.now().isoformat()
		})

	except Exception as e:
		logger.error(f"Error in get_active_permits: {e}")
		return jsonify({'status': 'error', 'message': str(e)}), 500


@permits_bp.route('/permits/company/<company_name>', methods=['GET'])
def get_permits_by_company(company_name):
	"""Get permits for a specific company."""
	try:
		company_name = urllib.parse.unquote(company_name)
		data = _get_cached_data()

		client = KLHKClient()
		company_permits = client.search_permits_by_company(company_name, data)

		return jsonify({
			'status': 'success',
			'data': company_permits,
			'company_name': company_name,
			'total_found': len(company_permits),
			'retrieved_at': datetime.now().isoformat()
		})

	except Exception as e:
		logger.error(f"Error in get_permits_by_company: {e}")
		return jsonify({'status': 'error', 'message': str(e)}), 500


@permits_bp.route('/permits/type/<permit_type>', methods=['GET'])
def get_permits_by_type(permit_type):
	"""Get permits by permit type."""
	try:
		permit_type = urllib.parse.unquote(permit_type)
		data = _get_cached_data()

		type_permits = []
		for permit in data:
			jenis = permit.get('jenis_layanan', '') or ''
			if permit_type.lower() in jenis.lower():
				type_permits.append(permit)

		return jsonify({
			'status': 'success',
			'data': type_permits,
			'permit_type': permit_type,
			'total_found': len(type_permits),
			'retrieved_at': datetime.now().isoformat()
		})

	except Exception as e:
		logger.error(f"Error in get_permits_by_type: {e}")
		return jsonify({'status': 'error', 'message': str(e)}), 500


@permits_bp.route('/permits/stats', methods=['GET'])
def get_permits_stats():
	"""Get statistics about permits data."""
	try:
		data = _get_cached_data()

		client = KLHKClient()
		total_permits = len(data)
		active_permits = len(client.filter_active_permits(data))

		type_counts = {}
		status_counts = {}
		for permit in data:
			jenis = permit.get('jenis_layanan', 'Unknown') or 'Unknown'
			type_counts[jenis] = type_counts.get(jenis, 0) + 1

			status = permit.get('status', 'Unknown') or 'Unknown'
			status_counts[status] = status_counts.get(status, 0) + 1

		return jsonify({
			'status': 'success',
			'statistics': {
				'total_permits': total_permits,
				'active_permits': active_permits,
				'inactive_permits': total_permits - active_permits,
				'by_permit_type': type_counts,
				'by_status': status_counts
			},
			'retrieved_at': datetime.now().isoformat()
		})

	except Exception as e:
		logger.error(f"Error in get_permits_stats: {e}")
		return jsonify({'status': 'error', 'message': str(e)}), 500
