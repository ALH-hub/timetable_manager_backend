from flask_sqlalchemy import SQLAlchemy
import os
from urllib.parse import quote_plus
from config.env import DATABASE_URL, SECRET_KEY

db = SQLAlchemy()

def _build_uri():
    # Prefer explicit full URL from environment (compose sets SQLALCHEMY_DATABASE_URI)
    direct = os.getenv("SQLALCHEMY_DATABASE_URI") or DATABASE_URL or os.getenv("DATABASE_URL")
    if direct:
        return direct
    user = os.getenv("DB_USER", "oumate")
    pwd = quote_plus(os.getenv("DB_PASSWORD", "oumate-psql123"))
    host = os.getenv("DB_HOST", "db")  # default to docker service name
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "timetable_manager")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{name}"

class Config:
    SECRET_KEY = SECRET_KEY
    SQLALCHEMY_DATABASE_URI = _build_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False