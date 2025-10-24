from flask_sqlalchemy import SQLAlchemy
from config.env import DATABASE_URL

db = SQLAlchemy()

class Config:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False