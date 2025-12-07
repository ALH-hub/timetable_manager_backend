"""
Services package
"""
from . import jwt_service
from . import level_service
from . import department_service
from . import teacher_service
from . import course_service
from . import room_service
from . import timetable_service
from . import slot_service

__all__ = [
    'jwt_service',
    'level_service',
    'department_service',
    'teacher_service',
    'course_service',
    'room_service',
    'timetable_service',
    'slot_service'
]