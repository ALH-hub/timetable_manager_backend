"""
Timetable service for business logic related to timetables
"""
from models.timetable import TimeTable, TimeTableSlot
from models.department import Department
from config.db import db
from datetime import datetime, date


VALID_STATUSES = ['draft', 'published', 'archived']


def get_all_timetables(department_id=None, status=None, academic_year=None, semester=None):
    """
    Get all timetables with optional filtering.

    Args:
        department_id: Optional filter by department
        status: Optional filter by status
        academic_year: Optional filter by academic year
        semester: Optional filter by semester

    Returns:
        Query object for timetables
    """
    query = TimeTable.query

    if department_id:
        query = query.filter_by(department_id=department_id)

    if status:
        query = query.filter_by(status=status)

    if academic_year:
        query = query.filter_by(academic_year=academic_year)

    if semester:
        query = query.filter_by(semester=semester)

    return query.order_by(TimeTable.created_at.desc())


def get_timetable_by_id(timetable_id):
    """
    Get a timetable by its ID.

    Args:
        timetable_id: The ID of the timetable

    Returns:
        TimeTable object or None
    """
    return TimeTable.query.get(timetable_id)


def create_timetable(name, department_id, week_start, week_end=None, academic_year=None,
                     semester=None, status='draft', created_by=None):
    """
    Create a new timetable.

    Args:
        name: Timetable name
        department_id: Department ID
        week_start: Week start date (date object or ISO string)
        week_end: Optional week end date
        academic_year: Optional academic year
        semester: Optional semester
        status: Status (default: 'draft')
        created_by: Admin ID who created it

    Returns:
        Tuple of (TimeTable object, error_message)
        If successful, error_message is None
    """
    try:
        # Check if department exists
        department = Department.query.get(department_id)
        if not department:
            return None, "Department not found"

        # Parse dates if strings
        if isinstance(week_start, str):
            week_start = date.fromisoformat(week_start)
        if week_end and isinstance(week_end, str):
            week_end = date.fromisoformat(week_end)

        # Validate week_end is after week_start
        if week_end and week_end <= week_start:
            return None, "Week end must be after week start"

        # Validate status
        if status not in VALID_STATUSES:
            return None, f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"

        timetable = TimeTable(
            name=name,
            department_id=department_id,
            week_start=week_start,
            week_end=week_end,
            academic_year=academic_year,
            semester=semester,
            status=status,
            created_by=created_by
        )

        db.session.add(timetable)
        db.session.commit()

        return timetable, None

    except ValueError as e:
        db.session.rollback()
        return None, f"Invalid date format: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating timetable: {str(e)}"


def update_timetable(timetable_id, **kwargs):
    """
    Update a timetable.

    Args:
        timetable_id: The ID of the timetable to update
        **kwargs: Fields to update

    Returns:
        Tuple of (TimeTable object, error_message)
        If successful, error_message is None
    """
    try:
        timetable = get_timetable_by_id(timetable_id)
        if not timetable:
            return None, "Timetable not found"

        # Check if department exists (if changing department)
        if 'department_id' in kwargs:
            department = Department.query.get(kwargs['department_id'])
            if not department:
                return None, "Department not found"

        # Parse dates if provided
        week_start = timetable.week_start
        week_end = timetable.week_end

        if 'week_start' in kwargs:
            if isinstance(kwargs['week_start'], str):
                week_start = date.fromisoformat(kwargs['week_start'])
            else:
                week_start = kwargs['week_start']

        if 'week_end' in kwargs:
            if kwargs['week_end'] is None:
                week_end = None
            elif isinstance(kwargs['week_end'], str):
                week_end = date.fromisoformat(kwargs['week_end'])
            else:
                week_end = kwargs['week_end']

            # Validate week_end is after week_start
            if week_end and week_end <= week_start:
                return None, "Week end must be after week start"

        # Validate status
        if 'status' in kwargs:
            if kwargs['status'] not in VALID_STATUSES:
                return None, f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"

        # Update fields
        if 'week_start' in kwargs:
            timetable.week_start = week_start
        if 'week_end' in kwargs:
            timetable.week_end = week_end

        for key, value in kwargs.items():
            if key not in ['week_start', 'week_end'] and hasattr(timetable, key):
                setattr(timetable, key, value)

        db.session.commit()
        return timetable, None

    except ValueError as e:
        db.session.rollback()
        return None, f"Invalid date format: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return None, f"Error updating timetable: {str(e)}"


def delete_timetable(timetable_id):
    """
    Delete a timetable and all its slots.

    Args:
        timetable_id: The ID of the timetable to delete

    Returns:
        Tuple of (success: bool, error_message, deleted_info)
    """
    try:
        timetable = get_timetable_by_id(timetable_id)
        if not timetable:
            return False, "Timetable not found", None

        timetable_name = timetable.name
        slots_count = len(timetable.slots)

        # The slots will be automatically deleted due to cascade='all, delete-orphan'
        db.session.delete(timetable)
        db.session.commit()

        return True, None, {
            'name': timetable_name,
            'slots_deleted': slots_count
        }

    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting timetable: {str(e)}", None


def publish_timetable(timetable_id):
    """
    Publish a timetable (change status to published).

    Args:
        timetable_id: The ID of the timetable

    Returns:
        Tuple of (TimeTable object, error_message)
        If successful, error_message is None
    """
    try:
        timetable = get_timetable_by_id(timetable_id)
        if not timetable:
            return None, "Timetable not found"

        if timetable.status == 'published':
            return None, "Timetable is already published"

        timetable.status = 'published'
        db.session.commit()

        return timetable, None

    except Exception as e:
        db.session.rollback()
        return None, f"Error publishing timetable: {str(e)}"


def archive_timetable(timetable_id):
    """
    Archive a timetable (change status to archived).

    Args:
        timetable_id: The ID of the timetable

    Returns:
        Tuple of (TimeTable object, error_message)
        If successful, error_message is None
    """
    try:
        timetable = get_timetable_by_id(timetable_id)
        if not timetable:
            return None, "Timetable not found"

        if timetable.status == 'archived':
            return None, "Timetable is already archived"

        timetable.status = 'archived'
        db.session.commit()

        return timetable, None

    except Exception as e:
        db.session.rollback()
        return None, f"Error archiving timetable: {str(e)}"


def clone_timetable(timetable_id, name, week_start=None, week_end=None, department_id=None,
                    academic_year=None, semester=None, created_by=None):
    """
    Create a copy of an existing timetable.

    Args:
        timetable_id: The ID of the timetable to clone
        name: Name for the cloned timetable
        week_start: Optional new week start date
        week_end: Optional new week end date
        department_id: Optional new department ID
        academic_year: Optional new academic year
        semester: Optional new semester
        created_by: Admin ID who created it

    Returns:
        Tuple of (TimeTable object, error_message)
        If successful, error_message is None
    """
    try:
        original = get_timetable_by_id(timetable_id)
        if not original:
            return None, "Timetable not found"

        # Use original values if not provided
        week_start = week_start or original.week_start
        week_end = week_end or original.week_end
        department_id = department_id or original.department_id
        academic_year = academic_year or original.academic_year
        semester = semester or original.semester

        # Parse dates if strings
        if isinstance(week_start, str):
            week_start = date.fromisoformat(week_start)
        if week_end and isinstance(week_end, str):
            week_end = date.fromisoformat(week_end)

        # Create new timetable
        new_timetable = TimeTable(
            name=name,
            department_id=department_id,
            week_start=week_start,
            week_end=week_end,
            academic_year=academic_year,
            semester=semester,
            status='draft',
            created_by=created_by
        )

        db.session.add(new_timetable)
        db.session.flush()

        # Clone all slots
        for original_slot in original.slots:
            new_slot = TimeTableSlot(
                timetable_id=new_timetable.id,
                course_id=original_slot.course_id,
                room_id=original_slot.room_id,
                day_of_week=original_slot.day_of_week,
                start_time=original_slot.start_time,
                end_time=original_slot.end_time,
                notes=original_slot.notes
            )
            db.session.add(new_slot)

        db.session.commit()

        return new_timetable, None

    except ValueError as e:
        db.session.rollback()
        return None, f"Invalid date format: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return None, f"Error cloning timetable: {str(e)}"


def get_timetable_stats(timetable_id):
    """
    Get statistics for a specific timetable.

    Args:
        timetable_id: The ID of the timetable

    Returns:
        Dictionary with statistics or None if timetable not found
    """
    timetable = get_timetable_by_id(timetable_id)
    if not timetable:
        return None

    total_slots = len(timetable.slots)
    unique_courses = len(set(slot.course_id for slot in timetable.slots))
    unique_rooms = len(set(slot.room_id for slot in timetable.slots))
    unique_teachers = len(set(slot.course.teacher_id for slot in timetable.slots
                              if slot.course and slot.course.teacher_id))

    # Slots per day
    slots_per_day = {}
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day_num in range(7):
        day_name = days[day_num]
        count = len([slot for slot in timetable.slots if slot.day_of_week == day_num])
        if count > 0:
            slots_per_day[day_name] = count

    # Total teaching hours
    total_minutes = sum(
        int((datetime.combine(date.min, slot.end_time) - datetime.combine(date.min, slot.start_time)).total_seconds() / 60)
        for slot in timetable.slots
        if slot.start_time and slot.end_time
    )
    total_hours = total_minutes / 60

    return {
        'timetable_id': timetable.id,
        'timetable_name': timetable.name,
        'statistics': {
            'total_slots': total_slots,
            'unique_courses': unique_courses,
            'unique_rooms': unique_rooms,
            'unique_teachers': unique_teachers,
            'total_teaching_hours': round(total_hours, 2),
            'slots_per_day': slots_per_day,
            'status': timetable.status
        }
    }


def serialize_timetable(timetable, include_slots=False):
    """
    Serialize a timetable object to dictionary.

    Args:
        timetable: TimeTable object
        include_slots: Boolean to include slots in response

    Returns:
        Dictionary representation of timetable
    """
    data = {
        'id': timetable.id,
        'name': timetable.name,
        'department_id': timetable.department_id,
        'department_name': timetable.department.name if timetable.department else None,
        'week_start': timetable.week_start.isoformat() if timetable.week_start else None,
        'week_end': timetable.week_end.isoformat() if timetable.week_end else None,
        'academic_year': timetable.academic_year,
        'semester': timetable.semester,
        'status': timetable.status,
        'created_by': timetable.created_by,
        'creator_name': timetable.creator.username if timetable.creator else None,
        'created_at': timetable.created_at.isoformat() if timetable.created_at else None,
        'updated_at': timetable.updated_at.isoformat() if timetable.updated_at else None,
        'slots_count': len(timetable.slots)
    }

    if include_slots:
        # Sort slots by day and time
        slots = sorted(timetable.slots, key=lambda x: (x.day_of_week, x.start_time))
        data['slots'] = [{
            'id': slot.id,
            'course_id': slot.course_id,
            'course_name': slot.course.name if slot.course else None,
            'course_code': slot.course.code if slot.course else None,
            'teacher_id': slot.course.teacher_id if slot.course else None,
            'teacher_name': slot.course.teacher.name if slot.course and slot.course.teacher else None,
            'room_id': slot.room_id,
            'room_name': slot.room.name if slot.room else None,
            'room_type': slot.room.room_type if slot.room else None,
            'room_capacity': slot.room.capacity if slot.room else None,
            'day_of_week': slot.day_of_week,
            'day_name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][slot.day_of_week],
            'start_time': slot.start_time.strftime('%H:%M') if slot.start_time else None,
            'end_time': slot.end_time.strftime('%H:%M') if slot.end_time else None,
            'duration_minutes': int((datetime.combine(date.min, slot.end_time) - datetime.combine(date.min, slot.start_time)).total_seconds() / 60) if slot.start_time and slot.end_time else None,
            'notes': slot.notes,
            'created_at': slot.created_at.isoformat() if slot.created_at else None,
            'updated_at': slot.updated_at.isoformat() if slot.updated_at else None
        } for slot in slots]

    return data

