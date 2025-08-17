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

# Tambahkan import blueprint health
from api.routes.health import health_bp
from api.routes.permits import permits_bp
from api.routes.global_data import global_bp

# Setup Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Daftarkan blueprint
app.register_blueprint(health_bp)
app.register_blueprint(permits_bp)
app.register_blueprint(global_bp)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inisialisasi status cache pada config (akan diupdate oleh service saat data diambil)
app.config.setdefault("CACHE_TIMESTAMP", None)

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
            '/permits/type/<permit_type>': 'Get permits by type',
            '/global/emissions': 'EPA emissions (filters: state, year, pollutant, page, limit)',
            '/global/emissions/stats': 'EPA emissions statistics',
            '/global/iso': 'ISO 14001 certifications (filters: country, limit)',
            '/global/eea': 'EEA indicators (filters: country, indicator, year, limit)',
            '/global/cevs/<company_name>': 'Compute CEVS score for a company (filters: country)'
        },
        'usage_examples': {
            'get_all_permits': '/permits',
            'search_company': '/permits/search?nama=PT%20Pertamina',
            'get_active_permits': '/permits/active',
            'company_specific': '/permits/company/PT%20Semen%20Indonesia',
            'by_permit_type': '/permits/type/Izin%20Lingkungan',
            'epa_emissions': '/global/emissions?state=TX&year=2023&pollutant=CO2',
            'iso_cert': '/global/iso?country=DE&limit=5',
            'eea_indicator': '/global/eea?country=SE&indicator=GHG&year=2023&limit=5',
            'cevs_company': '/global/cevs/Green%20Energy%20Co?country=US'
        }
    }
    return jsonify(api_info)

# Semua endpoint /permits telah dipindahkan ke blueprint routes.permits

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
            , '/global/emissions'
            , '/global/emissions/stats'
            , '/global/iso'
            , '/global/eea'
            , '/global/cevs/<company_name>'
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
