"""
Level service for business logic related to student levels
"""
from models.level import Level
from config.db import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func


def get_all_levels(active_only=False):
    """
    Get all levels, optionally filtered by active status.

    Args:
        active_only: If True, only return active levels

    Returns:
        Query object for levels
    """
    query = Level.query
    if active_only:
        query = query.filter_by(is_active=True)
    return query.order_by(Level.order)


def get_level_by_id(level_id):
    """
    Get a level by its ID.

    Args:
        level_id: The ID of the level

    Returns:
        Level object or None
    """
    return Level.query.get(level_id)


def get_level_by_code(code):
    """
    Get a level by its code.

    Args:
        code: The code of the level (e.g., "L1", "M1")

    Returns:
        Level object or None
    """
    return Level.query.filter_by(code=code).first()


def create_level(name, code, description=None, order=None, is_active=True):
    """
    Create a new level.

    Args:
        name: Level name (e.g., "Level 1")
        code: Level code (e.g., "L1")
        description: Optional description
        order: Order for sorting (if None, will be auto-assigned)
        is_active: Whether the level is active

    Returns:
        Tuple of (Level object, error_message)
        If successful, error_message is None
    """
    try:
        # Auto-assign order if not provided
        if order is None:
            max_order = db.session.query(func.max(Level.order)).scalar()
            order = (max_order or 0) + 1

        # Check if code already exists
        if get_level_by_code(code):
            return None, f"Level with code '{code}' already exists"

        # Check if name already exists
        if Level.query.filter_by(name=name).first():
            return None, f"Level with name '{name}' already exists"

        level = Level(
            name=name,
            code=code,
            description=description,
            order=order,
            is_active=is_active
        )

        db.session.add(level)
        db.session.commit()

        return level, None

    except IntegrityError as e:
        db.session.rollback()
        return None, f"Database integrity error: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating level: {str(e)}"


def update_level(level_id, **kwargs):
    """
    Update a level.

    Args:
        level_id: The ID of the level to update
        **kwargs: Fields to update (name, code, description, order, is_active)

    Returns:
        Tuple of (Level object, error_message)
        If successful, error_message is None
    """
    try:
        level = get_level_by_id(level_id)
        if not level:
            return None, "Level not found"

        # Check for code conflicts if code is being updated
        if 'code' in kwargs and kwargs['code'] != level.code:
            existing = get_level_by_code(kwargs['code'])
            if existing:
                return None, f"Level with code '{kwargs['code']}' already exists"

        # Check for name conflicts if name is being updated
        if 'name' in kwargs and kwargs['name'] != level.name:
            existing = Level.query.filter_by(name=kwargs['name']).first()
            if existing:
                return None, f"Level with name '{kwargs['name']}' already exists"

        # Update fields
        for key, value in kwargs.items():
            if hasattr(level, key):
                setattr(level, key, value)

        db.session.commit()
        return level, None

    except IntegrityError as e:
        db.session.rollback()
        return None, f"Database integrity error: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return None, f"Error updating level: {str(e)}"


def delete_level(level_id):
    """
    Delete a level.

    Args:
        level_id: The ID of the level to delete

    Returns:
        Tuple of (success: bool, error_message)
    """
    try:
        level = get_level_by_id(level_id)
        if not level:
            return False, "Level not found"

        # Check if level has associated courses
        if level.courses.count() > 0:
            return False, "Cannot delete level with associated courses. Please reassign or remove courses first."

        db.session.delete(level)
        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting level: {str(e)}"


def initialize_default_levels():
    """
    Initialize default levels if they don't exist.
    This can be used for seeding the database.

    Returns:
        List of created levels
    """
    default_levels = [
        {'name': 'Level 1', 'code': 'L1', 'order': 1, 'description': 'First year undergraduate level'},
        {'name': 'Level 2', 'code': 'L2', 'order': 2, 'description': 'Second year undergraduate level'},
        {'name': 'Level 3', 'code': 'L3', 'order': 3, 'description': 'Third year undergraduate level'},
        {'name': 'Master 1', 'code': 'M1', 'order': 4, 'description': 'First year master level'},
        {'name': 'Master 2', 'code': 'M2', 'order': 5, 'description': 'Second year master level'},
    ]

    created_levels = []
    for level_data in default_levels:
        existing = get_level_by_code(level_data['code'])
        if not existing:
            level, error = create_level(**level_data)
            if level:
                created_levels.append(level)

    return created_levels

