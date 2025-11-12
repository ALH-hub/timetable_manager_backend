from config.db import db
from datetime import datetime

class TimeTable(db.Model):
    __tablename__ = 'time_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Computer Science Fall 2024"
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    week_end = db.Column(db.Date)
    academic_year = db.Column(db.String(20))  # "2024-2025"
    semester = db.Column(db.String(20))  # "Fall", "Spring", "Summer"
    status = db.Column(db.String(20), default='draft')  # 'draft', 'published', 'archived'
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='timetables')
    creator = db.relationship('Admin', backref='created_timetables')
    slots = db.relationship('TimeTableSlot', backref='timetable', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TimeTable {self.name}>'

class TimeTableSlot(db.Model):
    __tablename__ = 'timetable_slot'

    id = db.Column(db.Integer, primary_key=True)
    timetable_id = db.Column(db.Integer, db.ForeignKey('time_table.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 1=Tuesday, etc. (more standardized)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', backref='timetable_slots')
    room = db.relationship('Room', backref='timetable_slots')

    # Constraint to prevent overlapping slots in the same room
    __table_args__ = (
        db.CheckConstraint('start_time < end_time', name='check_time_order'),
        db.CheckConstraint('day_of_week >= 0 AND day_of_week <= 6', name='check_valid_day')
    )

    def to_dict(self):
        return {
            'id': self.id,
            'timetable_id': self.timetable_id,
            'course_id': self.course_id,
            'room_id': self.room_id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<TimeTableSlot {self.course.code if self.course else "N/A"} on Day {self.day_of_week}>'

    @property
    def day_name(self):
        """Return human-readable day name"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[self.day_of_week] if 0 <= self.day_of_week <= 6 else 'Invalid Day'
