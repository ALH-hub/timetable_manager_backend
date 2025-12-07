"""
Teacher service for business logic related to teachers
"""
from models.teacher import Teacher
from models.department import Department
from models.timetable import TimeTableSlot
from config.db import db
from sqlalchemy.exc import IntegrityError


def get_all_teachers(department_id=None, is_active=None):
    """
    Get all teachers with optional filtering.

    Args:
        department_id: Optional filter by department
        is_active: Optional filter by active status

    Returns:
        Query object for teachers
    """
    query = Teacher.query

    if department_id:
        query = query.filter_by(department_id=department_id)

    if is_active is not None:
        query = query.filter_by(is_active=is_active)

    return query.order_by(Teacher.name)


def get_teacher_by_id(teacher_id):
    """
    Get a teacher by its ID.

    Args:
        teacher_id: The ID of the teacher

    Returns:
        Teacher object or None
    """
    return Teacher.query.get(teacher_id)


def create_teacher(name, email, department_id, phone=None, specialization=None, is_active=True):
    """
    Create a new teacher.

    Args:
        name: Teacher name
        email: Teacher email (must be unique)
        department_id: Department ID
        phone: Optional phone number
        specialization: Optional specialization
        is_active: Whether teacher is active

    Returns:
        Tuple of (Teacher object, error_message)
        If successful, error_message is None
    """
    try:
        # Check if department exists
        department = Department.query.get(department_id)
        if not department:
            return None, "Department not found"

        # Check if email already exists
        if Teacher.query.filter_by(email=email).first():
            return None, "Email already exists"

        teacher = Teacher(
            name=name,
            email=email,
            phone=phone,
            department_id=department_id,
            specialization=specialization,
            is_active=is_active
        )

        db.session.add(teacher)
        db.session.commit()

        return teacher, None

    except IntegrityError as e:
        db.session.rollback()
        return None, "Email already exists"
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating teacher: {str(e)}"


def update_teacher(teacher_id, **kwargs):
    """
    Update a teacher.

    Args:
        teacher_id: The ID of the teacher to update
        **kwargs: Fields to update (name, email, phone, department_id, specialization, is_active)

    Returns:
        Tuple of (Teacher object, error_message)
        If successful, error_message is None
    """
    try:
        teacher = get_teacher_by_id(teacher_id)
        if not teacher:
            return None, "Teacher not found"

        # Check if department exists (if changing department)
        if 'department_id' in kwargs:
            department = Department.query.get(kwargs['department_id'])
            if not department:
                return None, "Department not found"

        # Check for email conflicts if email is being updated
        if 'email' in kwargs and kwargs['email'] != teacher.email:
            existing = Teacher.query.filter_by(email=kwargs['email']).first()
            if existing:
                return None, "Email already exists"

        # Update fields
        for key, value in kwargs.items():
            if hasattr(teacher, key):
                setattr(teacher, key, value)

        db.session.commit()
        return teacher, None

    except IntegrityError as e:
        db.session.rollback()
        return None, "Email already exists"
    except Exception as e:
        db.session.rollback()
        return None, f"Error updating teacher: {str(e)}"


def delete_teacher(teacher_id):
    """
    Delete a teacher.

    Args:
        teacher_id: The ID of the teacher to delete

    Returns:
        Tuple of (success: bool, error_message)
    """
    try:
        teacher = get_teacher_by_id(teacher_id)
        if not teacher:
            return False, "Teacher not found"

        # Check if teacher has courses
        if teacher.courses:
            return False, "Cannot delete teacher with assigned courses. Please reassign courses first."

        db.session.delete(teacher)
        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting teacher: {str(e)}"


def get_teacher_schedule(teacher_id):
    """
    Get teacher's timetable schedule.

    Args:
        teacher_id: The ID of the teacher

    Returns:
        List of timetable slots for the teacher's courses
    """
    teacher = get_teacher_by_id(teacher_id)
    if not teacher:
        return None

    # Get all timetable slots for this teacher's courses
    from models.course import Course
    slots = TimeTableSlot.query.join(
        Course
    ).filter(
        Course.teacher_id == teacher_id
    ).all()

    return slots


def serialize_teacher(teacher, include_courses=False, include_schedule=False):
    """
    Serialize a teacher object to dictionary.

    Args:
        teacher: Teacher object
        include_courses: Whether to include courses list
        include_schedule: Whether to include schedule

    Returns:
        Dictionary representation of teacher
    """
    data = {
        'id': teacher.id,
        'name': teacher.name,
        'email': teacher.email,
        'phone': teacher.phone,
        'department_id': teacher.department_id,
        'department_name': teacher.department.name if teacher.department else None,
        'specialization': teacher.specialization,
        'is_active': teacher.is_active,
        'created_at': teacher.created_at.isoformat(),
        'updated_at': teacher.updated_at.isoformat()
    }

    if include_courses:
        data['courses'] = [{
            'id': course.id,
            'name': course.name,
            'code': course.code,
            'semester': course.semester,
            'year': course.year,
            'weekly_sessions': course.weekly_sessions,
            'is_active': course.is_active
        } for course in teacher.courses]
    else:
        data['courses_count'] = len(teacher.courses)

    if include_schedule:
        slots = get_teacher_schedule(teacher.id)
        data['schedule'] = [{
            'id': slot.id,
            'course_name': slot.course.name,
            'course_code': slot.course.code,
            'room_name': slot.room.name,
            'day_of_week': slot.day_of_week,
            'day_name': slot.day_name,
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M'),
            'notes': slot.notes,
            'timetable_name': slot.timetable.name
        } for slot in slots] if slots else []

    return data

