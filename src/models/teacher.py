from config import db
from .user import User

class Teacher(User):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'<Teacher {self.name}>'
