from config.db import db
from datetime import datetime

class TimeTable(db.Model):
    __tablename__ = 'time_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Computer Science Fall 2024"
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    week_end = db.Column(db.Date)
    academic_year = db.Column(db.String(20))  # "2024-2025"
    semester = db.Column(db.String(20))  # "Fall", "Spring", "Summer"
    status = db.Column(db.String(20), default='draft')  # 'draft', 'published', 'archived'
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='timetables')
    creator = db.relationship('Admin', backref='created_timetables')
    slots = db.relationship('TimeTableSlot', backref='timetable', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TimeTable {self.name}>'
