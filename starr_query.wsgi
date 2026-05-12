import sys
import os

# Add the app directory to Python's path
sys.path.insert(0, '/var/www/starr_query')

from app import app as application
