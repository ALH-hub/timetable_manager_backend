from config.db import db
from datetime import datetime

class TimeTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Computer Science Fall 2024"
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    week_start = db.Column(db.String(10), nullable=False)  # "2024-10-14"
    status = db.Column(db.String(20), default='draft')  # 'draft', 'published'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    department = db.relationship('Department', backref='timetables')
    slots = db.relationship('TimeTableSlot', backref='timetable', cascade='all, delete-orphan')
