"""
Flask API Server - Proxy untuk API PTSP MENLHK
MVP API yang bertindak sebagai perantara untuk mengakses data perizinan KLHK
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import os
import json
import urllib.parse

# Import client KLHK yang sudah kita buat
from klhk_client_fixed import KLHKClient

# Setup Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize KLHK client
klhk_client = KLHKClient()

# Cache untuk menyimpan data sementara (dalam produksi gunakan Redis/Memcached)
data_cache = {}
cache_timestamp = None
CACHE_DURATION = 3600  # 1 hour in seconds

def get_cached_data():
    """
    Get data from cache or fetch from KLHK API
    """
    global data_cache, cache_timestamp
    current_time = datetime.now().timestamp()
    
    # Check if cache is valid
    if cache_timestamp and (current_time - cache_timestamp < CACHE_DURATION):
        logger.info("Returning cached data")
        return data_cache
    
    logger.info("Fetching fresh data from KLHK API")
    
    # Try to get real data from KLHK API
    try:
        sk_data = klhk_client.get_status_sk(plain=False)
        
        if sk_data and isinstance(sk_data, list):
            formatted_data = klhk_client.format_permit_data(sk_data)
            data_cache = formatted_data
            cache_timestamp = current_time
            return formatted_data
        else:
            # If API fails, use sample data for demonstration
            logger.warning("KLHK API returned no data, using sample data")
            sample_data = klhk_client.create_sample_data()
            formatted_data = klhk_client.format_permit_data(sample_data)
            data_cache = formatted_data
            cache_timestamp = current_time
            return formatted_data
            
    except Exception as e:
        logger.error(f"Error fetching KLHK data: {e}")
        # Fallback to sample data
        sample_data = klhk_client.create_sample_data()
        formatted_data = klhk_client.format_permit_data(sample_data)
        data_cache = formatted_data
        cache_timestamp = current_time
        return formatted_data

@app.route('/', methods=['GET'])
def home():
    """
    API Documentation endpoint
    """
    api_info = {
        'name': 'KLHK Permit API Proxy',
        'version': '1.0.0',
        'description': 'API proxy untuk mengakses data perizinan PTSP MENLHK',
        'endpoints': {
            '/': 'API information',
            '/health': 'Health check',
            '/permits': 'Get all permits',
            '/permits/search': 'Search permits by company name',
            '/permits/active': 'Get active permits only',
            '/permits/company/<company_name>': 'Get permits for specific company',
            '/permits/type/<permit_type>': 'Get permits by type'
        },
        'usage_examples': {
            'get_all_permits': '/permits',
            'search_company': '/permits/search?nama=PT%20Pertamina',
            'get_active_permits': '/permits/active',
            'company_specific': '/permits/company/PT%20Semen%20Indonesia',
            'by_permit_type': '/permits/type/Izin%20Lingkungan'
        }
    }
    return jsonify(api_info)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_status': 'active' if cache_timestamp else 'empty',
        'last_updated': datetime.fromtimestamp(cache_timestamp).isoformat() if cache_timestamp else None
    })

@app.route('/permits', methods=['GET'])
def get_all_permits():
    """
    Get all permits with optional pagination
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 50
            
        # Get cached data
        data = get_cached_data()
        
        # Calculate pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_data = data[start_idx:end_idx]
        
        response = {
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
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in get_all_permits: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/permits/search', methods=['GET'])
def search_permits():
    """
    Search permits by company name or other parameters
    """
    try:
        # Get search parameters
        nama = request.args.get('nama', '').strip()
        jenis = request.args.get('jenis', '').strip()
        status = request.args.get('status', '').strip()
        
        if not any([nama, jenis, status]):
            return jsonify({
                'status': 'error',
                'message': 'At least one search parameter required (nama, jenis, or status)'
            }), 400
        
        # Get cached data
        data = get_cached_data()
        
        # Filter data based on search parameters
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
        
        response = {
            'status': 'success',
            'data': filtered_data,
            'search_params': {
                'nama': nama,
                'jenis': jenis,
                'status': status
            },
            'total_found': len(filtered_data),
            'retrieved_at': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in search_permits: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/permits/active', methods=['GET'])
def get_active_permits():
    """
    Get only active permits
    """
    try:
        # Get cached data
        data = get_cached_data()
        
        # Filter active permits
        active_permits = klhk_client.filter_active_permits(data)
        
        response = {
            'status': 'success',
            'data': active_permits,
            'total_active': len(active_permits),
            'total_all': len(data),
            'retrieved_at': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in get_active_permits: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/permits/company/<company_name>', methods=['GET'])
def get_permits_by_company(company_name):
    """
    Get permits for a specific company
    """
    try:
        # Decode URL-encoded company name
        company_name = urllib.parse.unquote(company_name)
        
        # Get cached data
        data = get_cached_data()
        
        # Search for company permits
        company_permits = klhk_client.search_permits_by_company(company_name, data)
        
        response = {
            'status': 'success',
            'data': company_permits,
            'company_name': company_name,
            'total_found': len(company_permits),
            'retrieved_at': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in get_permits_by_company: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/permits/type/<permit_type>', methods=['GET'])
def get_permits_by_type(permit_type):
    """
    Get permits by permit type
    """
    try:
        # Decode URL-encoded permit type
        permit_type = urllib.parse.unquote(permit_type)
        
        # Get cached data
        data = get_cached_data()
        
        # Filter by permit type
        type_permits = []
        for permit in data:
            jenis = permit.get('jenis_layanan', '') or ''
            if permit_type.lower() in jenis.lower():
                type_permits.append(permit)
        
        response = {
            'status': 'success',
            'data': type_permits,
            'permit_type': permit_type,
            'total_found': len(type_permits),
            'retrieved_at': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in get_permits_by_type: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/permits/stats', methods=['GET'])
def get_permits_stats():
    """
    Get statistics about permits data
    """
    try:
        # Get cached data
        data = get_cached_data()
        
        # Calculate statistics
        total_permits = len(data)
        active_permits = len(klhk_client.filter_active_permits(data))
        
        # Count by permit type
        type_counts = {}
        status_counts = {}
        
        for permit in data:
            # Count by type
            jenis = permit.get('jenis_layanan', 'Unknown') or 'Unknown'
            type_counts[jenis] = type_counts.get(jenis, 0) + 1
            
            # Count by status
            status = permit.get('status', 'Unknown') or 'Unknown'
            status_counts[status] = status_counts.get(status, 0) + 1
        
        response = {
            'status': 'success',
            'statistics': {
                'total_permits': total_permits,
                'active_permits': active_permits,
                'inactive_permits': total_permits - active_permits,
                'by_permit_type': type_counts,
                'by_status': status_counts
            },
            'retrieved_at': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in get_permits_stats: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'available_endpoints': [
            '/',
            '/health',
            '/permits',
            '/permits/search',
            '/permits/active',
            '/permits/company/<company_name>',
            '/permits/type/<permit_type>',
            '/permits/stats'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("="*60)
    print("🚀 KLHK Permit API Proxy Server")
    print("="*60)
    print(f"Server starting on http://localhost:{port}")
    print("Available endpoints:")
    print("  GET  /                     - API documentation")
    print("  GET  /health               - Health check")
    print("  GET  /permits              - Get all permits")
    print("  GET  /permits/search       - Search permits")
    print("  GET  /permits/active       - Get active permits")
    print("  GET  /permits/company/<name> - Get permits by company")
    print("  GET  /permits/type/<type>  - Get permits by type")
    print("  GET  /permits/stats        - Get permit statistics")
    print("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
