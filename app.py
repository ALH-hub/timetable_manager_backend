"""
Root-level runner for the Flask application
This file should be in the project root directory
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.flask import create_app
from src.config.db import db

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        import src.models
        db.create_all()

    app.run(debug=True)