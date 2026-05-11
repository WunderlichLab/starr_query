import sys
import os

# Add the app directory to Python's path
sys.path.insert(0, '/var/www/starr_query')

# Load .env if present
from dotenv import load_dotenv
load_dotenv('/var/www/starr_query/.env')

# Apache mod_wsgi looks for a callable named "application"
from app import app as application
