
from config import db
from datetime import datetime


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Computer Science"
    code = db.Column(db.String(10), unique=True, nullable=False)  # "CS"
    head = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
