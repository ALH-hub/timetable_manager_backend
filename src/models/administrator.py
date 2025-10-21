from .user import User

class Administrator(User):
    __tablename__ = 'administrators'

    def __repr__(self):
        return f'<Administrator {self.name}>'