"""
Department service for business logic related to departments
"""
from models.department import Department
from config.db import db
from sqlalchemy.exc import IntegrityError


def get_all_departments():
    """
    Get all departments.

    Returns:
        Query object for departments
    """
    return Department.query.order_by(Department.name)


def get_department_by_id(department_id):
    """
    Get a department by its ID.

    Args:
        department_id: The ID of the department

    Returns:
        Department object or None
    """
    return Department.query.get(department_id)


def create_department(name, code=None, head=None, contact_email=None):
    """
    Create a new department.

    Args:
        name: Department name
        code: Optional department code
        head: Optional department head name
        contact_email: Optional contact email

    Returns:
        Tuple of (Department object, error_message)
        If successful, error_message is None
    """
    try:
        # Check if department code already exists
        if code:
            existing = Department.query.filter_by(code=code).first()
            if existing:
                return None, f"Department with code '{code}' already exists"

        department = Department(
            name=name,
            code=code,
            head=head,
            contact_email=contact_email
        )

        db.session.add(department)
        db.session.commit()

        return department, None

    except IntegrityError as e:
        db.session.rollback()
        return None, f"Database integrity error: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating department: {str(e)}"


def update_department(department_id, **kwargs):
    """
    Update a department.

    Args:
        department_id: The ID of the department to update
        **kwargs: Fields to update (name, code, head, contact_email)

    Returns:
        Tuple of (Department object, error_message)
        If successful, error_message is None
    """
    try:
        department = get_department_by_id(department_id)
        if not department:
            return None, "Department not found"

        # Check for code conflicts if code is being updated
        if 'code' in kwargs and kwargs['code'] and kwargs['code'] != department.code:
            existing = Department.query.filter_by(code=kwargs['code']).first()
            if existing:
                return None, f"Department with code '{kwargs['code']}' already exists"

        # Update fields
        for key, value in kwargs.items():
            if hasattr(department, key):
                setattr(department, key, value)

        db.session.commit()
        return department, None

    except IntegrityError as e:
        db.session.rollback()
        return None, f"Database integrity error: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return None, f"Error updating department: {str(e)}"


def delete_department(department_id):
    """
    Delete a department.

    Args:
        department_id: The ID of the department to delete

    Returns:
        Tuple of (success: bool, error_message)
    """
    try:
        department = get_department_by_id(department_id)
        if not department:
            return False, "Department not found"

        # Check if department has teachers or courses
        if department.teachers or department.courses:
            return False, "Cannot delete department with associated teachers or courses"

        db.session.delete(department)
        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting department: {str(e)}"


def serialize_department(department, include_counts=False):
    """
    Serialize a department object to dictionary.

    Args:
        department: Department object
        include_counts: Whether to include counts of related entities

    Returns:
        Dictionary representation of department
    """
    data = {
        'id': department.id,
        'name': department.name,
        'code': department.code,
        'head': department.head,
        'contact_email': department.contact_email,
        'created_at': department.created_at.isoformat(),
        'updated_at': department.updated_at.isoformat()
    }

    if include_counts:
        data['teachers_count'] = len(department.teachers)
        data['courses_count'] = len(department.courses)
        data['timetables_count'] = len(department.timetables)

    return data

