"""
WSGI Application Entrypoint for Production Web Servers (Gunicorn / Waitress).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is explicitly loaded from project root
env_file = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_file)

from server.app import create_app
from server.config import ProductionConfig, DevelopmentConfig

env = os.getenv('FLASK_ENV', 'development')
config = ProductionConfig if env == 'production' else DevelopmentConfig

app = create_app(config_class=config)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
