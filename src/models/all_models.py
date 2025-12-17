"""
All Database Models - Combined File
====================================

This file contains all SQLAlchemy models for the Timetable Manager Backend.
All models are defined here for easy reference and documentation.

Models included:
- Admin: System administrators with authentication
- Department: Academic departments
- Level: Student academic levels (L1, L2, L3, M1, M2)
- Teacher: Faculty members
- Course: Academic courses
- Room: Physical spaces (classrooms, labs, lecture halls)
- TimeTable: Weekly schedules
- TimeTableSlot: Individual time slots
"""

from config.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================================
# ADMIN MODEL
# ============================================================================

class Admin(db.Model):
    """Administrator users with authentication capabilities."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='admin')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Set password hash from plain text password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'


# ============================================================================
# DEPARTMENT MODEL
# ============================================================================

class Department(db.Model):
    """Academic departments organizing courses and teachers."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=True)
    head = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Department {self.name} ({self.code})>'


# ============================================================================
# LEVEL MODEL
# ============================================================================

class Level(db.Model):
    """Student academic levels (Level 1, Level 2, Level 3, Master 1, Master 2)."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # "Level 1", "Level 2", "Level 3", "Master 1", "Master 2"
    code = db.Column(db.String(20), unique=True, nullable=False)  # "L1", "L2", "L3", "M1", "M2"
    description = db.Column(db.Text)  # Optional description
    order = db.Column(db.Integer, nullable=False)  # For sorting: 1, 2, 3, 4, 5
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    courses = db.relationship('Course', backref='level', lazy='dynamic')

    def to_dict(self):
        """Convert level to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'order': self.order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'courses_count': self.courses.count()
        }

    def __repr__(self):
        return f'<Level {self.name} ({self.code})>'


# ============================================================================
# TEACHER MODEL
# ============================================================================

class Teacher(db.Model):
    """Faculty members teaching courses."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Dr. Smith"
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    specialization = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='teachers')

    def __repr__(self):
        return f'<Teacher {self.name}>'


# ============================================================================
# COURSE MODEL
# ============================================================================

class Course(db.Model):
    """Academic courses with scheduling requirements."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Introduction to Programming"
    code = db.Column(db.String(20), unique=True, nullable=False)   # "CS101" - Made unique
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)  # Made required
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'))  # Optional level assignment
    weekly_sessions = db.Column(db.Integer, default=1)
    semester = db.Column(db.String(20))  # "Fall 2024", "Spring 2025"
    year = db.Column(db.Integer)  # Academic year
    is_active = db.Column(db.Boolean, default=True)  # For course status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='courses')
    teacher = db.relationship('Teacher', backref='courses')

    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'


# ============================================================================
# ROOM MODEL
# ============================================================================

class Room(db.Model):
    """Physical spaces for classes (classrooms, labs, lecture halls)."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    room_type = db.Column(db.String(30), nullable=False)  # "classroom", "lab", "lecture_hall"
    capacity = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=True)  # For maintenance/availability status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Room {self.name} ({self.room_type})>'


# ============================================================================
# TIMETABLE MODEL
# ============================================================================

class TimeTable(db.Model):
    """Container for weekly schedules."""
    __tablename__ = 'time_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Computer Science Fall 2024"
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=True)
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
    level = db.relationship('Level', backref='timetables')
    creator = db.relationship('Admin', backref='created_timetables')
    slots = db.relationship('TimeTableSlot', backref='timetable', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TimeTable {self.name}>'


# ============================================================================
# TIMETABLE SLOT MODEL
# ============================================================================

class TimeTableSlot(db.Model):
    """Individual scheduled time slots."""
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
        """Convert slot to dictionary for JSON serialization"""
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

