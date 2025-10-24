from config.db import db

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)

    # Define the relationship with the Teacher model
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)

    def __repr__(self):
        return f'<Course {self.name}>'
