from config.db import db
from datetime import datetime

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Introduction to Programming"
    code = db.Column(db.String(20), unique=True, nullable=False)   # "CS101" - Made unique
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)  # Made required
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'))  # Optional level assignment
    weekly_sessions = db.Column(db.Integer, default=1)
    semester = db.Column(db.String(20))  # "Fall 2024", "Spring 2025"
    year = db.Column(db.Integer)  # Academic year
    is_active = db.Column(db.Boolean, default=True)  # For course status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='courses')
    teacher = db.relationship('Teacher', backref='courses')

    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'
