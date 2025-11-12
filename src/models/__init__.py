from .admin import Admin
from .classroom import Room  # Note: classroom.py defines Room class
from .teacher import Teacher
from .course import Course
from .department import Department
from .timetable import TimeTable, TimeTableSlot

__all__ = [
    'Admin',
    'Room',
    'Teacher',
    'Course',
    'Department',
    'TimeTable',
    'TimeTableSlot'
]