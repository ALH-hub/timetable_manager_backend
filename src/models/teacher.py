from config import db
from .user import User

class Teacher(User):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    course = db.relationship('courses', backref='teacher')

    def __repr__(self):
        return f'<Teacher {self.name}>'
