from config.db import db
from datetime import datetime

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Introduction to Programming"
    code = db.Column(db.String(20), nullable=False)   # "CS101"
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    duration = db.Column(db.Integer, nullable=False)  # minutes
    weekly_sessions = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    department = db.relationship('Department', backref='courses')
    teacher = db.relationship('Teacher', backref='courses')
