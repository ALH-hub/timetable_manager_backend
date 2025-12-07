"""
Room service for business logic related to rooms
"""
from models.classroom import Room
from models.timetable import TimeTableSlot
from config.db import db
from sqlalchemy.exc import IntegrityError
from datetime import time


VALID_ROOM_TYPES = ['classroom', 'lab', 'lecture_hall']


def get_all_rooms(room_type=None, is_available=None, min_capacity=None, max_capacity=None):
    """
    Get all rooms with optional filtering.

    Args:
        room_type: Optional filter by room type
        is_available: Optional filter by availability
        min_capacity: Optional minimum capacity filter
        max_capacity: Optional maximum capacity filter

    Returns:
        Query object for rooms
    """
    query = Room.query

    if room_type:
        query = query.filter_by(room_type=room_type)

    if is_available is not None:
        query = query.filter_by(is_available=is_available)

    if min_capacity:
        query = query.filter(Room.capacity >= min_capacity)

    if max_capacity:
        query = query.filter(Room.capacity <= max_capacity)

    return query.order_by(Room.name)


def get_room_by_id(room_id):
    """
    Get a room by its ID.

    Args:
        room_id: The ID of the room

    Returns:
        Room object or None
    """
    return Room.query.get(room_id)


def create_room(name, room_type, capacity, is_available=True):
    """
    Create a new room.

    Args:
        name: Room name (must be unique)
        room_type: Room type (classroom, lab, lecture_hall)
        capacity: Room capacity (positive integer)
        is_available: Whether room is available

    Returns:
        Tuple of (Room object, error_message)
        If successful, error_message is None
    """
    try:
        # Validate room type
        if room_type not in VALID_ROOM_TYPES:
            return None, f"Invalid room type. Must be one of: {', '.join(VALID_ROOM_TYPES)}"

        # Validate capacity
        if not isinstance(capacity, int) or capacity <= 0:
            return None, "Capacity must be a positive integer"

        # Check if room name already exists
        if Room.query.filter_by(name=name).first():
            return None, "Room name already exists"

        room = Room(
            name=name,
            room_type=room_type,
            capacity=capacity,
            is_available=is_available
        )

        db.session.add(room)
        db.session.commit()

        return room, None

    except IntegrityError as e:
        db.session.rollback()
        return None, "Room name already exists"
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating room: {str(e)}"


def update_room(room_id, **kwargs):
    """
    Update a room.

    Args:
        room_id: The ID of the room to update
        **kwargs: Fields to update (name, room_type, capacity, is_available)

    Returns:
        Tuple of (Room object, error_message)
        If successful, error_message is None
    """
    try:
        room = get_room_by_id(room_id)
        if not room:
            return None, "Room not found"

        # Validate room type if provided
        if 'room_type' in kwargs:
            if kwargs['room_type'] not in VALID_ROOM_TYPES:
                return None, f"Invalid room type. Must be one of: {', '.join(VALID_ROOM_TYPES)}"

        # Validate capacity if provided
        if 'capacity' in kwargs:
            if not isinstance(kwargs['capacity'], int) or kwargs['capacity'] <= 0:
                return None, "Capacity must be a positive integer"

        # Check for name conflicts if name is being updated
        if 'name' in kwargs and kwargs['name'] != room.name:
            existing = Room.query.filter_by(name=kwargs['name']).first()
            if existing:
                return None, "Room name already exists"

        # Update fields
        for key, value in kwargs.items():
            if hasattr(room, key):
                setattr(room, key, value)

        db.session.commit()
        return room, None

    except IntegrityError as e:
        db.session.rollback()
        return None, "Room name already exists"
    except Exception as e:
        db.session.rollback()
        return None, f"Error updating room: {str(e)}"


def delete_room(room_id):
    """
    Delete a room.

    Args:
        room_id: The ID of the room to delete

    Returns:
        Tuple of (success: bool, error_message)
    """
    try:
        room = get_room_by_id(room_id)
        if not room:
            return False, "Room not found"

        # Check if room has timetable slots
        if room.timetable_slots:
            return False, "Cannot delete room with scheduled classes. Please remove all schedules first."

        db.session.delete(room)
        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting room: {str(e)}"


def get_room_schedule(room_id, timetable_id=None):
    """
    Get room's schedule.

    Args:
        room_id: The ID of the room
        timetable_id: Optional filter by timetable

    Returns:
        List of timetable slots for the room
    """
    query = TimeTableSlot.query.filter_by(room_id=room_id)

    if timetable_id:
        query = query.filter_by(timetable_id=timetable_id)

    return query.order_by(TimeTableSlot.day_of_week, TimeTableSlot.start_time).all()


def check_room_availability(day_of_week, start_time_str, end_time_str, room_type=None, min_capacity=None):
    """
    Check room availability for a specific time slot.

    Args:
        day_of_week: Day of week (0-6)
        start_time_str: Start time in HH:MM format
        end_time_str: End time in HH:MM format
        room_type: Optional filter by room type
        min_capacity: Optional minimum capacity filter

    Returns:
        Tuple of (list of available rooms, error_message)
        If successful, error_message is None
    """
    try:
        # Parse time strings
        try:
            start_time = time.fromisoformat(start_time_str)
            end_time = time.fromisoformat(end_time_str)
        except ValueError:
            return None, "Invalid time format. Use HH:MM format."

        # Build query for available rooms
        query = Room.query.filter_by(is_available=True)

        if room_type:
            query = query.filter_by(room_type=room_type)

        if min_capacity:
            query = query.filter(Room.capacity >= min_capacity)

        all_rooms = query.all()

        # Check which rooms are available at the specified time
        available_rooms = []
        for room in all_rooms:
            # Check for conflicting slots
            conflicting_slots = TimeTableSlot.query.filter(
                TimeTableSlot.room_id == room.id,
                TimeTableSlot.day_of_week == day_of_week,
                TimeTableSlot.start_time < end_time,
                TimeTableSlot.end_time > start_time
            ).first()

            if not conflicting_slots:
                available_rooms.append({
                    'id': room.id,
                    'name': room.name,
                    'room_type': room.room_type,
                    'capacity': room.capacity
                })

        return available_rooms, None

    except Exception as e:
        return None, f"Error checking availability: {str(e)}"


def serialize_room(room, include_schedule=False, timetable_id=None):
    """
    Serialize a room object to dictionary.

    Args:
        room: Room object
        include_schedule: Whether to include schedule
        timetable_id: Optional filter schedule by timetable

    Returns:
        Dictionary representation of room
    """
    data = {
        'id': room.id,
        'name': room.name,
        'room_type': room.room_type,
        'capacity': room.capacity,
        'is_available': room.is_available,
        'created_at': room.created_at.isoformat(),
        'updated_at': room.updated_at.isoformat()
    }

    if include_schedule:
        slots = get_room_schedule(room.id, timetable_id)
        data['current_schedule'] = [{
            'id': slot.id,
            'course_name': slot.course.name,
            'course_code': slot.course.code,
            'day_of_week': slot.day_of_week,
            'day_name': slot.day_name,
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M'),
            'timetable_name': slot.timetable.name
        } for slot in slots]

    return data

