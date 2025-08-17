from flask import Blueprint, jsonify, current_app
from datetime import datetime

health_bp = Blueprint("health_bp", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    cache_timestamp = current_app.config.get("CACHE_TIMESTAMP")
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_status": "active" if cache_timestamp else "empty",
        "last_updated": datetime.fromtimestamp(cache_timestamp).isoformat() if cache_timestamp else None,
    })