"""
Admin routes for API key management and system monitoring.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request, g
from datetime import datetime
import logging
from typing import Any, Dict, List

from api.utils.security import (
    require_api_key, 
    generate_api_key, 
    list_api_keys,
    validate_api_key,
    VALID_API_KEYS
)

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")
logger = logging.getLogger(__name__)

@admin_bp.route("/api-keys", methods=["GET"])
@require_api_key
def list_keys():
    """List all registered API keys (admin only)."""
    # Check if client has admin privileges (premium tier for now)
    if g.client_info.get("tier") != "premium":
        return jsonify({
            "status": "error", 
            "message": "Admin privileges required"
        }), 403
    
    keys = list_api_keys()
    return jsonify({
        "status": "success",
        "data": {
            "api_keys": keys,
            "total_count": len(keys)
        },
        "timestamp": datetime.now().isoformat()
    })

@admin_bp.route("/api-keys", methods=["POST"])
@require_api_key
def create_key():
    """Create a new API key."""
    # Check admin privileges
    if g.client_info.get("tier") != "premium":
        return jsonify({
            "status": "error",
            "message": "Admin privileges required"
        }), 403
    
    data = request.get_json() or {}
    client_name = data.get("client_name")
    tier = data.get("tier", "basic")
    
    if not client_name:
        return jsonify({
            "status": "error",
            "message": "client_name is required"
        }), 400
    
    if tier not in ["basic", "premium"]:
        return jsonify({
            "status": "error", 
            "message": "tier must be 'basic' or 'premium'"
        }), 400
    
    try:
        new_key = generate_api_key(client_name, tier)
        return jsonify({
            "status": "success",
            "data": {
                "api_key": new_key,
                "client_name": client_name,
                "tier": tier,
                "created": datetime.now().isoformat(),
                "requests_per_minute": 30 if tier == "basic" else 100
            },
            "message": "API key created successfully"
        })
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to create API key"
        }), 500

@admin_bp.route("/api-keys/<key_prefix>", methods=["DELETE"])
@require_api_key  
def delete_key(key_prefix: str):
    """Delete an API key (by key prefix)."""
    # Check admin privileges
    if g.client_info.get("tier") != "premium":
        return jsonify({
            "status": "error",
            "message": "Admin privileges required"
        }), 403
    
    # Find key by prefix
    key_to_delete = None
    for key in VALID_API_KEYS:
        if key.startswith(key_prefix):
            key_to_delete = key
            break
    
    if not key_to_delete:
        return jsonify({
            "status": "error",
            "message": "API key not found"
        }), 404
    
    # Don't allow deleting the current key
    if key_to_delete == g.api_key:
        return jsonify({
            "status": "error",
            "message": "Cannot delete the key currently being used"
        }), 400
    
    # Delete the key
    deleted_info = VALID_API_KEYS.pop(key_to_delete)
    
    return jsonify({
        "status": "success",
        "message": f"API key for '{deleted_info['name']}' deleted successfully"
    })

@admin_bp.route("/stats", methods=["GET"])
@require_api_key
def api_stats():
    """Get API usage statistics."""
    if g.client_info.get("tier") != "premium":
        return jsonify({
            "status": "error",
            "message": "Admin privileges required" 
        }), 403
    
    return jsonify({
        "status": "success",
        "data": {
            "total_api_keys": len(VALID_API_KEYS),
            "tiers": {
                "basic": len([k for k, v in VALID_API_KEYS.items() if v.get("tier") == "basic"]),
                "premium": len([k for k, v in VALID_API_KEYS.items() if v.get("tier") == "premium"])
            },
            "system_info": {
                "version": "1.0.0",
                "environment": "development"
            }
        },
        "timestamp": datetime.now().isoformat()
    })

__all__ = ["admin_bp"]
