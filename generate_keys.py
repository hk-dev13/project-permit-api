#!/usr/bin/env python3
"""
Generate secure API keys for production use
"""

import secrets
import hashlib
import string
import json
from datetime import datetime

def generate_api_key(prefix="", length=32):
    """Generate a cryptographically secure API key."""
    alphabet = string.ascii_letters + string.digits
    key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"{prefix}_{key}" if prefix else key

def generate_tier_keys():
    """Generate API keys for different tiers."""
    keys = {
        "basic": {
            "key": generate_api_key("basic", 40),
            "tier": "basic",
            "rate_limit": "100/hour",
            "features": ["emissions", "countries", "basic_stats"]
        },
        "premium": {
            "key": generate_api_key("premium", 40), 
            "tier": "premium",
            "rate_limit": "1000/hour",
            "features": ["emissions", "countries", "stats", "analytics", "bulk_export"]
        },
        "enterprise": {
            "key": generate_api_key("enterprise", 40),
            "tier": "enterprise", 
            "rate_limit": "unlimited",
            "features": ["all"]
        }
    }
    
    # Generate master key
    master_key = generate_api_key("master", 48)
    
    return keys, master_key

def create_env_format(keys, master_key):
    """Create environment variable format."""
    key_strings = []
    for tier_name, tier_data in keys.items():
        key_strings.append(f"{tier_data['key']}:Production{tier_name.title()}:{tier_name}")
    
    api_keys_env = ",".join(key_strings)
    
    return f"""# Production API Keys - Generated {datetime.now().isoformat()}
API_KEYS={api_keys_env}
MASTER_API_KEY={master_key}

# Individual Keys for Reference:
# Basic Tier: {keys['basic']['key']}
# Premium Tier: {keys['premium']['key']} 
# Enterprise Tier: {keys['enterprise']['key']}
# Master Key: {master_key}
"""

if __name__ == "__main__":
    print("🔑 Generating secure API keys for production...")
    
    keys, master_key = generate_tier_keys()
    env_content = create_env_format(keys, master_key)
    
    # Save to file
    with open('.env.production.keys', 'w') as f:
        f.write(env_content)
    
    # Save detailed info to JSON
    key_info = {
        "generated_at": datetime.now().isoformat(),
        "keys": keys,
        "master_key": master_key,
        "usage_instructions": {
            "basic": "For standard API usage with rate limits",
            "premium": "For high-volume usage with extended features", 
            "enterprise": "For unlimited usage with all features",
            "master": "For administrative access and service management"
        }
    }
    
    with open('production_keys.json', 'w') as f:
        json.dump(key_info, f, indent=2)
    
    print("✅ API Keys generated successfully!")
    print("\n📁 Files created:")
    print("- .env.production.keys (Environment variables)")
    print("- production_keys.json (Detailed key information)")
    
    print("\n🔐 Security Notes:")
    print("- Store these keys securely")
    print("- Never commit keys to version control")
    print("- Update GitHub Secrets with new API_KEYS value")
    print("- Rotate keys regularly")
    
    print(f"\n📋 Quick Reference:")
    print(f"Basic Key: {keys['basic']['key']}")
    print(f"Premium Key: {keys['premium']['key']}")
    print(f"Master Key: {master_key}")
