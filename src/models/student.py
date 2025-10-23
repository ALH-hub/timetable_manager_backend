from config import db
from .user import User

class Student(User):
    __tablename__ = 'students'

    def __repr__(self):
        return f'<Student {self.name}>'
