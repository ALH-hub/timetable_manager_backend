from .admin import Admin
from .classroom import Room  # Note: classroom.py defines Room class
from .teacher import Teacher
from .course import Course
from .department import Department
from .timetable import TimeTable

# Import the slot model - note the file is named 'timetable-slot'
import importlib.util
import sys
import os

# Dynamically import the timetable-slot module
spec = importlib.util.spec_from_file_location("timetable_slot",
    os.path.join(os.path.dirname(__file__), "timetable-slot"))
timetable_slot_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(timetable_slot_module)
TimeTableSlot = timetable_slot_module.TimeTableSlot

__all__ = [
    'Admin',
    'Room',
    'Teacher',
    'Course',
    'Department',
    'TimeTable',
    'TimeTableSlot'
]