"""
Security and authentication middleware for the Permit API.
"""
from __future__ import annotations

import os
import hashlib
import hmac
import logging
from functools import wraps
from typing import Any, Dict, Optional, Set
from datetime import datetime, timedelta
import time

from flask import request, jsonify, g

logger = logging.getLogger(__name__)

# Simple rate limiting using in-memory storage
_rate_limit_storage = {}

def simple_rate_limit(key: str, limit: int, window: int = 60) -> bool:
    """Simple in-memory rate limiting."""
    now = time.time()
    
    # Clean old entries
    _rate_limit_storage[key] = [
        timestamp for timestamp in _rate_limit_storage.get(key, [])
        if now - timestamp < window
    ]
    
    # Check current rate
    current_count = len(_rate_limit_storage.get(key, []))
    
    if current_count >= limit:
        return False
    
    # Record this request
    if key not in _rate_limit_storage:
        _rate_limit_storage[key] = []
    _rate_limit_storage[key].append(now)
    
    return True

# Valid API keys (in production, store these in a secure database)
# Format: {api_key: {"name": "client_name", "tier": "basic|premium", "created": datetime}}
VALID_API_KEYS: Dict[str, Dict[str, Any]] = {
    # Development/demo keys (to be removed in production)
    "demo_key_basic_2025": {
        "name": "Demo Client Basic", 
        "tier": "basic", 
        "created": datetime.now(),
        "requests_per_minute": 30
    },
    "demo_key_premium_2025": {
        "name": "Demo Client Premium", 
        "tier": "premium", 
        "created": datetime.now(),
        "requests_per_minute": 100
    }
}

# Load API keys from environment if available
def load_api_keys_from_env():
    """Load API keys from environment variables."""
    env_keys = os.getenv("API_KEYS", "")
    if env_keys:
        try:
            # Format: "key1:name1:tier1,key2:name2:tier2"
            for key_config in env_keys.split(","):
                parts = key_config.strip().split(":")
                if len(parts) >= 3:
                    key, name, tier = parts[0], parts[1], parts[2]
                    rpm = 30 if tier == "basic" else 100
                    VALID_API_KEYS[key] = {
                        "name": name,
                        "tier": tier,
                        "created": datetime.now(),
                        "requests_per_minute": rpm
                    }
        except Exception as e:
            logger.error(f"Error loading API keys from environment: {e}")

# Load keys from environment on startup
load_api_keys_from_env()

def validate_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Validate API key and return client info if valid.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        Client info dict if valid, None if invalid
    """
    if not api_key:
        return None
    
    # Check against known keys
    if api_key in VALID_API_KEYS:
        return VALID_API_KEYS[api_key]
    
    # Check against environment-based keys
    env_master_key = os.getenv("MASTER_API_KEY")
    if env_master_key and hmac.compare_digest(api_key, env_master_key):
        return {
            "name": "Master Client",
            "tier": "premium", 
            "created": datetime.now(),
            "requests_per_minute": 200
        }
    
    return None

def require_api_key(f):
    """
    Decorator to require valid API key for endpoint access.
    
    Usage:
        @app.route('/protected')
        @require_api_key
        def protected_endpoint():
            # Access client info via g.client_info
            return {"message": f"Hello {g.client_info['name']}"}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in various locations
        api_key = None
        
        # 1. Authorization header (Bearer token)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header[7:]
        
        # 2. X-API-Key header
        if not api_key:
            api_key = request.headers.get('X-API-Key')
        
        # 3. Query parameter (less secure, for development)
        if not api_key:
            api_key = request.args.get('api_key')
        
        if not api_key:
            return jsonify({
                "status": "error",
                "message": "API key required. Include it in Authorization header (Bearer token), X-API-Key header, or api_key parameter.",
                "code": "MISSING_API_KEY"
            }), 401
        
        # Validate the key
        client_info = validate_api_key(api_key)
        if not client_info:
            return jsonify({
                "status": "error",
                "message": "Invalid API key",
                "code": "INVALID_API_KEY"
            }), 401
        
        # Store client info for use in the endpoint
        g.client_info = client_info
        g.api_key = api_key
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_rate_limit_for_key() -> str:
    """Get rate limit based on client tier."""
    if hasattr(g, 'client_info'):
        rpm = g.client_info.get('requests_per_minute', 30)
        return f"{rpm} per minute"
    return "30 per minute"

def setup_rate_limiting(app):
    """Setup simple rate limiting middleware."""
    
    @app.before_request
    def check_rate_limit():
        """Check rate limit for API requests."""
        if not request.path.startswith('/global'):
            return
        
        # Get client info or default
        client_info = getattr(g, 'client_info', {'requests_per_minute': 30})
        api_key = getattr(g, 'api_key', request.remote_addr)
        limit = client_info.get('requests_per_minute', 30)
        
        if not simple_rate_limit(api_key, limit, 60):
            return jsonify({
                "status": "error",
                "message": f"Rate limit exceeded: {limit} requests per minute",
                "code": "RATE_LIMIT_EXCEEDED",
                "retry_after": 60
            }), 429
    
    return None  # No limiter object needed

def generate_api_key(client_name: str, tier: str = "basic") -> str:
    """Generate a new API key for a client."""
    # In production, this should be cryptographically secure
    timestamp = datetime.now().isoformat()
    raw_key = f"{client_name}_{tier}_{timestamp}"
    api_key = hashlib.sha256(raw_key.encode()).hexdigest()[:32]
    
    # Store in memory (in production, store in database)
    VALID_API_KEYS[api_key] = {
        "name": client_name,
        "tier": tier,
        "created": datetime.now(),
        "requests_per_minute": 30 if tier == "basic" else 100
    }
    
    return api_key

def list_api_keys() -> Dict[str, Dict[str, Any]]:
    """List all registered API keys (for admin purposes)."""
    # Remove sensitive keys from response
    safe_keys = {}
    for key, info in VALID_API_KEYS.items():
        safe_keys[key[:8] + "..."] = {
            "name": info["name"],
            "tier": info["tier"],
            "created": info["created"].isoformat() if isinstance(info["created"], datetime) else info["created"],
            "requests_per_minute": info.get("requests_per_minute", 30)
        }
    return safe_keys

# Public/open endpoints that don't require API key
PUBLIC_ENDPOINTS: Set[str] = {
    "/health",
    "/",
    "/api/docs",
    "/docs"
}

def is_public_endpoint(endpoint: str) -> bool:
    """Check if an endpoint is public and doesn't require API key."""
    return endpoint in PUBLIC_ENDPOINTS or endpoint.startswith("/static")

__all__ = [
    "require_api_key", 
    "setup_rate_limiting", 
    "validate_api_key",
    "generate_api_key",
    "list_api_keys",
    "get_rate_limit_for_key",
    "is_public_endpoint"
]
