from config.db import db
from datetime import datetime

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # "A101", "Lab B"
    room_type = db.Column(db.String(30), nullable=False)  # "classroom", "lab", "lecture_hall"
    capacity = db.Column(db.Integer, nullable=False)
    equipment = db.Column(db.String(200))  # "projector,whiteboard,computers"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
