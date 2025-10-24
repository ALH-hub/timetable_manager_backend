from config.db import db
from .user import User

class Teacher(User):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    course = db.relationship('Course', backref='teacher')

    __mapper_args__ = {
        'polymorphic_identity': 'teacher',
    }

    def __repr__(self):
        return f'<Teacher {self.name}>'
