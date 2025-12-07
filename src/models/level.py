from config.db import db
from datetime import datetime

class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # "Level 1", "Level 2", "Level 3", "Master 1", "Master 2"
    code = db.Column(db.String(20), unique=True, nullable=False)  # "L1", "L2", "L3", "M1", "M2"
    description = db.Column(db.Text)  # Optional description
    order = db.Column(db.Integer, nullable=False)  # For sorting: 1, 2, 3, 4, 5
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    courses = db.relationship('Course', backref='level', lazy='dynamic')

    def to_dict(self):
        """Convert level to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'order': self.order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'courses_count': self.courses.count()
        }

    def __repr__(self):
        return f'<Level {self.name} ({self.code})>'

