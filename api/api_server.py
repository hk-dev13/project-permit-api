"""
Flask API Server - Environmental Data Verification API
Production-ready API with security, caching, and multi-source data integration
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import logging
from datetime import datetime
import os
import json
import urllib.parse
from dotenv import load_dotenv

# Load environment variables (will load .env.production in production)
load_dotenv()

# Import security utilities
from api.utils.security import setup_rate_limiting, require_api_key, is_public_endpoint

# Import all blueprints
from api.routes.health import health_bp
from api.routes.permits import permits_bp
from api.routes.global_data import global_bp
from api.routes.admin import admin_bp

# Setup Flask app with production configuration
app = Flask(__name__)

# Production CORS configuration
cors_origins = os.getenv('CORS_ORIGINS', '*')
if cors_origins != '*':
    cors_origins = cors_origins.split(',')

CORS(app, 
     origins=cors_origins,
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-API-Key'])

# Production logging configuration
log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.getenv('LOG_FILE', 'app.log'), mode='a')
    ] if os.getenv('LOG_FILE') else [logging.StreamHandler()]
)

# Setup rate limiting
limiter = setup_rate_limiting(app)

# Daftarkan blueprint
app.register_blueprint(health_bp)
app.register_blueprint(permits_bp)
app.register_blueprint(global_bp)
app.register_blueprint(admin_bp)

# Security middleware
@app.before_request
def check_api_key():
    """Check API key for protected endpoints."""
    endpoint = request.endpoint
    if endpoint and not is_public_endpoint(request.path):
        # Skip API key check for public endpoints
        if request.path in ['/health', '/', '/docs']:
            return
        
        # For now, make global routes require API key while keeping permits open
        if request.path.startswith('/global'):
            # Extract API key from request
            api_key = None
            
            # Check Authorization header (Bearer token)
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                api_key = auth_header[7:]
            
            # Check X-API-Key header
            if not api_key:
                api_key = request.headers.get('X-API-Key')
            
            # Check query parameter (for development)
            if not api_key:
                api_key = request.args.get('api_key')
            
            if not api_key:
                return jsonify({
                    "status": "error",
                    "message": "API key required for global data access. Include it in Authorization header (Bearer token), X-API-Key header, or api_key parameter.",
                    "code": "MISSING_API_KEY",
                    "demo_keys": {
                        "basic": "demo_key_basic_2025",
                        "premium": "demo_key_premium_2025"
                    }
                }), 401
            
            # Validate API key
            from api.utils.security import validate_api_key
            client_info = validate_api_key(api_key)
            if not client_info:
                return jsonify({
                    "status": "error",
                    "message": "Invalid API key",
                    "code": "INVALID_API_KEY"
                }), 401
            
            # Store client info for rate limiting and logging
            g.client_info = client_info
            g.api_key = api_key

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
            '/global/cevs/<company_name>': 'Compute CEVS score for a company (filters: country)',
            '/global/edgar': 'EDGAR series+trend (params: country, pollutant=PM2.5, window=3)'
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
            , '/global/edgar'
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
