from flask import Blueprint, jsonify, current_app
import os
import sys
from datetime import datetime

health_bp = Blueprint("health_bp", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Comprehensive health check for AWS App Runner and monitoring.
    Returns detailed system status information.
    """
    cache_timestamp = current_app.config.get("CACHE_TIMESTAMP")
    
    # Check system status
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": os.getenv("FLASK_ENV", "development"),
        "python_version": sys.version.split()[0],
        "system": {
            "cache_status": "active" if cache_timestamp else "empty",
            "last_cache_update": datetime.fromtimestamp(cache_timestamp).isoformat() if cache_timestamp else None,
        },
        "services": {
            "api_server": "running",
            "security": "enabled" if os.getenv("API_KEYS") else "disabled",
            "rate_limiting": "active"
        }
    }
    
    # Add detailed info for development/staging
    if os.getenv("FLASK_ENV") != "production":
        health_status["debug"] = {
            "port": os.getenv("PORT", "5000"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "demo_keys_available": bool(os.getenv("API_KEYS", "").find("demo_key") >= 0)
        }
    
    return jsonify(health_status), 200

@health_bp.route("/ready", methods=["GET"])  
def readiness_check():
    """
    Kubernetes/container readiness check.
    Simple endpoint that returns 200 when service is ready to accept traffic.
    """
    return jsonify({"status": "ready"}), 200

@health_bp.route("/live", methods=["GET"])
def liveness_check():
    """
    Kubernetes/container liveness check.
    Simple endpoint that returns 200 when service is alive.
    """
    return jsonify({"status": "alive"}), 200