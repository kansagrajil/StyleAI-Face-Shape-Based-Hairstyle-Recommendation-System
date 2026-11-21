"""
WSGI entry point for Gunicorn.
Usage: gunicorn server.wsgi:app -w 4 -b 0.0.0.0:5000
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
