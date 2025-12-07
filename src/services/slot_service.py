"""
Slot service for business logic related to timetable slots
"""
from models.timetable import TimeTableSlot, TimeTable
from models.course import Course
from models.classroom import Room
from config.db import db
from datetime import time


def get_all_slots(timetable_id=None, course_id=None, room_id=None, day_of_week=None):
    """
    Get all timetable slots with optional filtering.

    Args:
        timetable_id: Optional filter by timetable
        course_id: Optional filter by course
        room_id: Optional filter by room
        day_of_week: Optional filter by day (0-6)

    Returns:
        Query object for slots
    """
    query = TimeTableSlot.query

    if timetable_id:
        query = query.filter_by(timetable_id=timetable_id)

    if course_id:
        query = query.filter_by(course_id=course_id)

    if room_id:
        query = query.filter_by(room_id=room_id)

    if day_of_week is not None:
        query = query.filter_by(day_of_week=day_of_week)

    return query.order_by(TimeTableSlot.day_of_week, TimeTableSlot.start_time)


def get_slot_by_id(slot_id):
    """
    Get a slot by its ID.

    Args:
        slot_id: The ID of the slot

    Returns:
        TimeTableSlot object or None
    """
    return TimeTableSlot.query.get(slot_id)


def create_slot(timetable_id, course_id, room_id, day_of_week, start_time_str, end_time_str, notes=None):
    """
    Create a new timetable slot.

    Args:
        timetable_id: Timetable ID
        course_id: Course ID
        room_id: Room ID
        day_of_week: Day of week (0-6)
        start_time_str: Start time in HH:MM format
        end_time_str: End time in HH:MM format
        notes: Optional notes

    Returns:
        Tuple of (TimeTableSlot object, error_message)
        If successful, error_message is None
    """
    try:
        # Validate foreign keys exist
        timetable = TimeTable.query.get(timetable_id)
        if not timetable:
            return None, "Timetable not found"

        course = Course.query.get(course_id)
        if not course:
            return None, "Course not found"

        room = Room.query.get(room_id)
        if not room:
            return None, "Room not found"

        # Validate day_of_week
        if not isinstance(day_of_week, int) or day_of_week < 0 or day_of_week > 6:
            return None, "day_of_week must be an integer between 0 (Monday) and 6 (Sunday)"

        # Parse and validate times
        try:
            start_time = time.fromisoformat(start_time_str)
            end_time = time.fromisoformat(end_time_str)
        except ValueError:
            return None, "Invalid time format. Use HH:MM format."

        if start_time >= end_time:
            return None, "Start time must be before end time"

        # Check if room is available
        if not room.is_available:
            return None, "Room is not available"

        # Check for conflicts - room double booking
        room_conflict = TimeTableSlot.query.filter(
            TimeTableSlot.room_id == room_id,
            TimeTableSlot.day_of_week == day_of_week,
            TimeTableSlot.start_time < end_time,
            TimeTableSlot.end_time > start_time
        ).first()

        if room_conflict:
            return None, f"Room conflict: {room.name} is already booked at this time"

        # Check for teacher conflicts (if course has a teacher)
        if course.teacher_id:
            teacher_conflict = TimeTableSlot.query.join(Course).filter(
                Course.teacher_id == course.teacher_id,
                TimeTableSlot.day_of_week == day_of_week,
                TimeTableSlot.start_time < end_time,
                TimeTableSlot.end_time > start_time
            ).first()

            if teacher_conflict:
                return None, f"Teacher conflict: {course.teacher.name} is already scheduled at this time"

        # Create new slot
        slot = TimeTableSlot(
            timetable_id=timetable_id,
            course_id=course_id,
            room_id=room_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            notes=notes
        )

        db.session.add(slot)
        db.session.commit()

        return slot, None

    except Exception as e:
        db.session.rollback()
        return None, f"Error creating slot: {str(e)}"


def update_slot(slot_id, timetable_id=None, course_id=None, room_id=None, day_of_week=None,
                start_time_str=None, end_time_str=None, notes=None):
    """
    Update a timetable slot.

    Args:
        slot_id: The ID of the slot to update
        timetable_id: Optional new timetable ID
        course_id: Optional new course ID
        room_id: Optional new room ID
        day_of_week: Optional new day of week
        start_time_str: Optional new start time (HH:MM format)
        end_time_str: Optional new end time (HH:MM format)
        notes: Optional new notes

    Returns:
        Tuple of (TimeTableSlot object, error_message)
        If successful, error_message is None
    """
    try:
        slot = get_slot_by_id(slot_id)
        if not slot:
            return None, "Slot not found"

        # Validate foreign keys if provided
        if timetable_id:
            timetable = TimeTable.query.get(timetable_id)
            if not timetable:
                return None, "Timetable not found"

        if course_id:
            course = Course.query.get(course_id)
            if not course:
                return None, "Course not found"

        if room_id:
            room = Room.query.get(room_id)
            if not room:
                return None, "Room not found"
            if not room.is_available:
                return None, "Room is not available"

        # Validate day_of_week if provided
        if day_of_week is not None:
            if not isinstance(day_of_week, int) or day_of_week < 0 or day_of_week > 6:
                return None, "day_of_week must be an integer between 0 (Monday) and 6 (Sunday)"

        # Parse and validate times if provided
        start_time = slot.start_time
        end_time = slot.end_time

        if start_time_str:
            try:
                start_time = time.fromisoformat(start_time_str)
            except ValueError:
                return None, "Invalid start_time format. Use HH:MM format."

        if end_time_str:
            try:
                end_time = time.fromisoformat(end_time_str)
            except ValueError:
                return None, "Invalid end_time format. Use HH:MM format."

        if start_time >= end_time:
            return None, "Start time must be before end time"

        # Check for conflicts if time/room/day is being changed
        final_room_id = room_id if room_id else slot.room_id
        final_day_of_week = day_of_week if day_of_week is not None else slot.day_of_week

        if (room_id or day_of_week or start_time_str or end_time_str):
            # Check for room conflicts (excluding current slot)
            room_conflict = TimeTableSlot.query.filter(
                TimeTableSlot.id != slot_id,
                TimeTableSlot.room_id == final_room_id,
                TimeTableSlot.day_of_week == final_day_of_week,
                TimeTableSlot.start_time < end_time,
                TimeTableSlot.end_time > start_time
            ).first()

            if room_conflict:
                room_obj = Room.query.get(final_room_id)
                return None, f"Room conflict: {room_obj.name} is already booked at this time"

        # Check for teacher conflicts if course is being changed
        final_course_id = course_id if course_id else slot.course_id
        if course_id or day_of_week or start_time_str or end_time_str:
            course_obj = Course.query.get(final_course_id)
            if course_obj and course_obj.teacher_id:
                teacher_conflict = TimeTableSlot.query.join(Course).filter(
                    TimeTableSlot.id != slot_id,
                    Course.teacher_id == course_obj.teacher_id,
                    TimeTableSlot.day_of_week == final_day_of_week,
                    TimeTableSlot.start_time < end_time,
                    TimeTableSlot.end_time > start_time
                ).first()

                if teacher_conflict:
                    return None, f"Teacher conflict: {course_obj.teacher.name} is already scheduled at this time"

        # Update fields
        if timetable_id:
            slot.timetable_id = timetable_id
        if course_id:
            slot.course_id = course_id
        if room_id:
            slot.room_id = room_id
        if day_of_week is not None:
            slot.day_of_week = day_of_week
        if start_time_str:
            slot.start_time = start_time
        if end_time_str:
            slot.end_time = end_time
        if notes is not None:
            slot.notes = notes

        db.session.commit()
        return slot, None

    except Exception as e:
        db.session.rollback()
        return None, f"Error updating slot: {str(e)}"


def delete_slot(slot_id):
    """
    Delete a timetable slot.

    Args:
        slot_id: The ID of the slot to delete

    Returns:
        Tuple of (success: bool, error_message)
    """
    try:
        slot = get_slot_by_id(slot_id)
        if not slot:
            return False, "Slot not found"

        db.session.delete(slot)
        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting slot: {str(e)}"


def check_conflicts(course_id, room_id, day_of_week, start_time_str, end_time_str):
    """
    Check for scheduling conflicts for a proposed time slot.

    Args:
        course_id: Course ID
        room_id: Room ID
        day_of_week: Day of week (0-6)
        start_time_str: Start time in HH:MM format
        end_time_str: End time in HH:MM format

    Returns:
        Tuple of (list of conflicts, error_message)
        If successful, error_message is None
    """
    try:
        # Parse times
        try:
            start_time = time.fromisoformat(start_time_str)
            end_time = time.fromisoformat(end_time_str)
        except ValueError:
            return None, "Invalid time format. Use HH:MM format."

        if start_time >= end_time:
            return None, "Start time must be before end time"

        conflicts = []

        # Check room conflicts
        room_conflicts = TimeTableSlot.query.filter(
            TimeTableSlot.room_id == room_id,
            TimeTableSlot.day_of_week == day_of_week,
            TimeTableSlot.start_time < end_time,
            TimeTableSlot.end_time > start_time
        ).all()

        for conflict in room_conflicts:
            conflicts.append({
                'type': 'room',
                'message': f'Room {conflict.room.name} is already booked',
                'conflicting_slot': {
                    'id': conflict.id,
                    'course_name': conflict.course.name,
                    'start_time': conflict.start_time.strftime('%H:%M'),
                    'end_time': conflict.end_time.strftime('%H:%M'),
                    'timetable_name': conflict.timetable.name
                }
            })

        # Check teacher conflicts
        course = Course.query.get(course_id)
        if course and course.teacher_id:
            teacher_conflicts = TimeTableSlot.query.join(Course).filter(
                Course.teacher_id == course.teacher_id,
                TimeTableSlot.day_of_week == day_of_week,
                TimeTableSlot.start_time < end_time,
                TimeTableSlot.end_time > start_time
            ).all()

            for conflict in teacher_conflicts:
                conflicts.append({
                    'type': 'teacher',
                    'message': f'Teacher {course.teacher.name} is already scheduled',
                    'conflicting_slot': {
                        'id': conflict.id,
                        'course_name': conflict.course.name,
                        'room_name': conflict.room.name,
                        'start_time': conflict.start_time.strftime('%H:%M'),
                        'end_time': conflict.end_time.strftime('%H:%M'),
                        'timetable_name': conflict.timetable.name
                    }
                })

        return conflicts, None

    except Exception as e:
        return None, f"Error checking conflicts: {str(e)}"


def bulk_create_slots(timetable_id, slots_data):
    """
    Create multiple timetable slots at once.

    Args:
        timetable_id: Timetable ID
        slots_data: List of slot data dictionaries

    Returns:
        Tuple of (list of created slots, list of errors)
    """
    created_slots = []
    errors = []

    for i, slot_data in enumerate(slots_data):
        try:
            # Validate required fields
            required_fields = ['course_id', 'room_id', 'day_of_week', 'start_time', 'end_time']
            for field in required_fields:
                if field not in slot_data:
                    errors.append(f'Slot {i+1}: {field} is required')
                    break
            else:
                # All required fields present, try to create slot
                slot, error = create_slot(
                    timetable_id=timetable_id,
                    course_id=slot_data['course_id'],
                    room_id=slot_data['room_id'],
                    day_of_week=slot_data['day_of_week'],
                    start_time_str=slot_data['start_time'],
                    end_time_str=slot_data['end_time'],
                    notes=slot_data.get('notes')
                )

                if error:
                    errors.append(f'Slot {i+1}: {error}')
                else:
                    created_slots.append(slot)
        except Exception as e:
            errors.append(f'Slot {i+1}: {str(e)}')

    if errors:
        db.session.rollback()
    else:
        db.session.commit()

    return created_slots, errors


def serialize_slot(slot):
    """
    Serialize a slot object to dictionary.

    Args:
        slot: TimeTableSlot object

    Returns:
        Dictionary representation of slot
    """
    return {
        'id': slot.id,
        'timetable_id': slot.timetable_id,
        'timetable_name': slot.timetable.name if slot.timetable else None,
        'course_id': slot.course_id,
        'course_name': slot.course.name if slot.course else None,
        'course_code': slot.course.code if slot.course else None,
        'teacher_name': slot.course.teacher.name if slot.course and slot.course.teacher else None,
        'level_id': slot.course.level_id if slot.course else None,
        'level_name': slot.course.level.name if slot.course and slot.course.level else None,
        'level_code': slot.course.level.code if slot.course and slot.course.level else None,
        'room_id': slot.room_id,
        'room_name': slot.room.name if slot.room else None,
        'day_of_week': slot.day_of_week,
        'day_name': slot.day_name,
        'start_time': slot.start_time.strftime('%H:%M') if slot.start_time else None,
        'end_time': slot.end_time.strftime('%H:%M') if slot.end_time else None,
        'notes': slot.notes,
        'created_at': slot.created_at.isoformat() if slot.created_at else None,
        'updated_at': slot.updated_at.isoformat() if slot.updated_at else None
    }

