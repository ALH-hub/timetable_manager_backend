"""
Course service for business logic related to courses
"""
from models.course import Course
from models.department import Department
from models.teacher import Teacher
from models.level import Level
from config.db import db
from sqlalchemy.exc import IntegrityError


def get_all_courses(department_id=None, teacher_id=None, level_id=None, semester=None, year=None, is_active=None):
    """
    Get all courses with optional filtering.

    Args:
        department_id: Optional filter by department
        teacher_id: Optional filter by teacher
        level_id: Optional filter by level
        semester: Optional filter by semester
        year: Optional filter by year
        is_active: Optional filter by active status

    Returns:
        Query object for courses
    """
    query = Course.query

    if department_id:
        query = query.filter_by(department_id=department_id)

    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)

    if level_id:
        query = query.filter_by(level_id=level_id)

    if semester:
        query = query.filter_by(semester=semester)

    if year:
        query = query.filter_by(year=year)

    if is_active is not None:
        query = query.filter_by(is_active=is_active)

    return query.order_by(Course.code)


def get_course_by_id(course_id):
    """
    Get a course by its ID.

    Args:
        course_id: The ID of the course

    Returns:
        Course object or None
    """
    return Course.query.get(course_id)


def create_course(name, code, department_id, teacher_id=None, level_id=None, weekly_sessions=1,
                  semester=None, year=None, is_active=True):
    """
    Create a new course.

    Args:
        name: Course name
        code: Course code (must be unique)
        department_id: Department ID
        teacher_id: Optional teacher ID
        level_id: Optional level ID
        weekly_sessions: Number of weekly sessions (default: 1)
        semester: Optional semester
        year: Optional academic year
        is_active: Whether course is active

    Returns:
        Tuple of (Course object, error_message)
        If successful, error_message is None
    """
    try:
        # Check if department exists
        department = Department.query.get(department_id)
        if not department:
            return None, "Department not found"

        # Check if teacher exists and belongs to correct department (if provided)
        if teacher_id:
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                return None, "Teacher not found"
            if teacher.department_id != department_id:
                return None, "Teacher must belong to the same department"

        # Check if level exists (if provided)
        if level_id:
            level = Level.query.get(level_id)
            if not level:
                return None, "Level not found"

        # Check if course code already exists
        if Course.query.filter_by(code=code).first():
            return None, "Course code already exists"

        # Validate weekly_sessions
        if not isinstance(weekly_sessions, int) or weekly_sessions <= 0:
            return None, "Weekly sessions must be a positive integer"

        course = Course(
            name=name,
            code=code,
            department_id=department_id,
            teacher_id=teacher_id,
            level_id=level_id,
            weekly_sessions=weekly_sessions,
            semester=semester,
            year=year,
            is_active=is_active
        )

        db.session.add(course)
        db.session.commit()

        return course, None

    except IntegrityError as e:
        db.session.rollback()
        return None, "Course code already exists"
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating course: {str(e)}"


def update_course(course_id, **kwargs):
    """
    Update a course.

    Args:
        course_id: The ID of the course to update
        **kwargs: Fields to update

    Returns:
        Tuple of (Course object, error_message)
        If successful, error_message is None
    """
    try:
        course = get_course_by_id(course_id)
        if not course:
            return None, "Course not found"

        # Check if department exists (if changing department)
        if 'department_id' in kwargs:
            department = Department.query.get(kwargs['department_id'])
            if not department:
                return None, "Department not found"

        # Check if teacher exists and belongs to correct department (if changing teacher)
        if 'teacher_id' in kwargs:
            if kwargs['teacher_id']:  # If not None
                teacher = Teacher.query.get(kwargs['teacher_id'])
                if not teacher:
                    return None, "Teacher not found"

                # Use the department from kwargs if provided, otherwise current course department
                dept_id = kwargs.get('department_id', course.department_id)
                if teacher.department_id != dept_id:
                    return None, "Teacher must belong to the same department"

        # Check if level exists (if changing level)
        if 'level_id' in kwargs:
            if kwargs['level_id']:  # If not None
                level = Level.query.get(kwargs['level_id'])
                if not level:
                    return None, "Level not found"

        # Check if course code already exists (if changing code)
        if 'code' in kwargs and kwargs['code'] != course.code:
            existing = Course.query.filter_by(code=kwargs['code']).first()
            if existing:
                return None, "Course code already exists"

        # Validate weekly_sessions if provided
        if 'weekly_sessions' in kwargs:
            if not isinstance(kwargs['weekly_sessions'], int) or kwargs['weekly_sessions'] <= 0:
                return None, "Weekly sessions must be a positive integer"

        # Update fields
        for key, value in kwargs.items():
            if hasattr(course, key):
                setattr(course, key, value)

        db.session.commit()
        return course, None

    except IntegrityError as e:
        db.session.rollback()
        return None, "Course code already exists"
    except Exception as e:
        db.session.rollback()
        return None, f"Error updating course: {str(e)}"


def delete_course(course_id):
    """
    Delete a course.

    Args:
        course_id: The ID of the course to delete

    Returns:
        Tuple of (success: bool, error_message)
    """
    try:
        course = get_course_by_id(course_id)
        if not course:
            return False, "Course not found"

        # Check if course has timetable slots
        if course.timetable_slots:
            return False, "Cannot delete course with scheduled classes. Please remove all schedules first."

        db.session.delete(course)
        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting course: {str(e)}"


def assign_teacher_to_course(course_id, teacher_id):
    """
    Assign a teacher to a course.

    Args:
        course_id: The ID of the course
        teacher_id: The ID of the teacher

    Returns:
        Tuple of (Course object, error_message)
        If successful, error_message is None
    """
    try:
        course = get_course_by_id(course_id)
        if not course:
            return None, "Course not found"

        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return None, "Teacher not found"

        # Check if teacher belongs to the same department
        if teacher.department_id != course.department_id:
            return None, "Teacher must belong to the same department as the course"

        # Check if teacher is active
        if not teacher.is_active:
            return None, "Cannot assign inactive teacher"

        course.teacher_id = teacher_id
        db.session.commit()

        return course, None

    except Exception as e:
        db.session.rollback()
        return None, f"Error assigning teacher: {str(e)}"


def unassign_teacher_from_course(course_id):
    """
    Unassign teacher from a course.

    Args:
        course_id: The ID of the course

    Returns:
        Tuple of (Course object, error_message)
        If successful, error_message is None
    """
    try:
        course = get_course_by_id(course_id)
        if not course:
            return None, "Course not found"

        course.teacher_id = None
        db.session.commit()

        return course, None

    except Exception as e:
        db.session.rollback()
        return None, f"Error unassigning teacher: {str(e)}"


def serialize_course(course, include_schedule=False):
    """
    Serialize a course object to dictionary.

    Args:
        course: Course object
        include_schedule: Whether to include timetable slots

    Returns:
        Dictionary representation of course
    """
    data = {
        'id': course.id,
        'name': course.name,
        'code': course.code,
        'department_id': course.department_id,
        'department_name': course.department.name if course.department else None,
        'teacher_id': course.teacher_id,
        'teacher_name': course.teacher.name if course.teacher else None,
        'teacher_email': course.teacher.email if course.teacher else None,
        'level_id': course.level_id,
        'level_name': course.level.name if course.level else None,
        'level_code': course.level.code if course.level else None,
        'weekly_sessions': course.weekly_sessions,
        'semester': course.semester,
        'year': course.year,
        'is_active': course.is_active,
        'created_at': course.created_at.isoformat(),
        'updated_at': course.updated_at.isoformat()
    }

    if include_schedule:
        slots = course.timetable_slots
        data['schedule'] = [{
            'id': slot.id,
            'room_name': slot.room.name,
            'room_id': slot.room_id,
            'day_of_week': slot.day_of_week,
            'day_name': slot.day_name,
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M'),
            'notes': slot.notes,
            'timetable_id': slot.timetable_id,
            'timetable_name': slot.timetable.name
        } for slot in slots]

    return data

