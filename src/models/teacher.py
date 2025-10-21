from src.config import db
from .user import User

class Teacher(User):
    __tablename__ = 'teachers'

    def __repr__(self):
        return f'<Teacher {self.name}>'
