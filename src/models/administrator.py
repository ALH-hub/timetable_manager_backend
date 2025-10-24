from .user import User
from config.db import db

class Administrator(User):
    __tablename__ = 'administrators'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'administrator',
    }

    def __repr__(self):
        return f'<Administrator {self.name}>'