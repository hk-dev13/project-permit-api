#!/usr/bin/env python
"""
Production startup script for the Permit API.
Optimized for AWS App Runner and other cloud platforms.
"""
import os
import sys

# Add the project root to Python path
try:
    project_root = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Handle case when __file__ is not defined (exec context)
    project_root = os.getcwd()

sys.path.insert(0, project_root)

def main():
    """Main application entry point."""
    from api.api_server import app
    
    # Configure for production
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    env = os.environ.get('FLASK_ENV', 'development')
    
    print(f"Starting Permit API on port {port}")
    print(f"Environment: {env}")
    print(f"Debug mode: {debug}")
    print(f"Project root: {project_root}")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )

if __name__ == '__main__':
    main()
