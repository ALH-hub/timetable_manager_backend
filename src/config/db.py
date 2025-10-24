from flask_sqlalchemy import SQLAlchemy
from config.env import DATABASE_URL, SECRET_KEY

db = SQLAlchemy()

class Config:
    SECRET_KEY = SECRET_KEY
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False