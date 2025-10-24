from config.db import db
from .user import User

class Student(User):
    __tablename__ = 'students'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

    def __repr__(self):
        return f'<Student {self.name}>'
