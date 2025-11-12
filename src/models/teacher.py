from config.db import db
from datetime import datetime
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Dr. Smith"
    email = db.Column(db.String(120))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    specialization = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    department = db.relationship('Department', backref='teachers')
