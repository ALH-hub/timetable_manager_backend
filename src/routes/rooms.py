from flask import Blueprint, request, jsonify
from models.classroom import Room
from config.db import db
from services.jwt_service import token_required
from sqlalchemy.exc import IntegrityError

rooms_bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')


@rooms_bp.route('/', methods=['GET'])
@token_required
def get_rooms(current_admin):
    """Get all rooms with optional filtering."""
    try:
        # Get query parameters
        room_type = request.args.get('room_type')
        is_available = request.args.get('is_available', type=bool)
        min_capacity = request.args.get('min_capacity', type=int)
        max_capacity = request.args.get('max_capacity', type=int)

        # Build query
        query = Room.query

        if room_type:
            query = query.filter_by(room_type=room_type)

        if is_available is not None:
            query = query.filter_by(is_available=is_available)

        if min_capacity:
            query = query.filter(Room.capacity >= min_capacity)

        if max_capacity:
            query = query.filter(Room.capacity <= max_capacity)

        rooms = query.order_by(Room.name).all()

        return jsonify({
            'rooms': [{
                'id': room.id,
                'name': room.name,
                'room_type': room.room_type,
                'capacity': room.capacity,
                'is_available': room.is_available,
                'created_at': room.created_at.isoformat(),
                'updated_at': room.updated_at.isoformat()
            } for room in rooms]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rooms_bp.route('/', methods=['POST'])
@token_required
def create_room(current_admin):
    """Create a new room."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'room_type', 'capacity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Validate room type
        valid_room_types = ['classroom', 'lab', 'lecture_hall']
        if data['room_type'] not in valid_room_types:
            return jsonify({
                'error': f'Invalid room type. Must be one of: {", ".join(valid_room_types)}'
            }), 400

        # Validate capacity
        if not isinstance(data['capacity'], int) or data['capacity'] <= 0:
            return jsonify({'error': 'Capacity must be a positive integer'}), 400

        # Check if room name already exists
        if Room.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Room name already exists'}), 400

        # Create new room
        room = Room(
            name=data['name'],
            room_type=data['room_type'],
            capacity=data['capacity'],
            is_available=data.get('is_available', True)
        )

        db.session.add(room)
        db.session.commit()

        return jsonify({
            'message': 'Room created successfully',
            'room': {
                'id': room.id,
                'name': room.name,
                'room_type': room.room_type,
                'capacity': room.capacity,
                'is_available': room.is_available,
                'created_at': room.created_at.isoformat(),
                'updated_at': room.updated_at.isoformat()
            }
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Room name already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@rooms_bp.route('/<int:room_id>', methods=['GET'])
@token_required
def get_room(current_admin, room_id):
    """Get a specific room."""
    try:
        room = Room.query.get_or_404(room_id)

        # Get current timetable slots for this room
        from models.timetable import TimeTableSlot
        current_slots = TimeTableSlot.query.filter_by(room_id=room_id).all()

        return jsonify({
            'room': {
                'id': room.id,
                'name': room.name,
                'room_type': room.room_type,
                'capacity': room.capacity,
                'is_available': room.is_available,
                'created_at': room.created_at.isoformat(),
                'updated_at': room.updated_at.isoformat(),
                'current_schedule': [{
                    'id': slot.id,
                    'course_name': slot.course.name,
                    'course_code': slot.course.code,
                    'day_of_week': slot.day_of_week,
                    'day_name': slot.day_name,
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M'),
                    'timetable_name': slot.timetable.name
                } for slot in current_slots]
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rooms_bp.route('/<int:room_id>', methods=['PUT'])
@token_required
def update_room(current_admin, room_id):
    """Update a room."""
    try:
        room = Room.query.get_or_404(room_id)
        data = request.get_json()

        # Validate room type if provided
        if 'room_type' in data:
            valid_room_types = ['classroom', 'lab', 'lecture_hall']
            if data['room_type'] not in valid_room_types:
                return jsonify({
                    'error': f'Invalid room type. Must be one of: {", ".join(valid_room_types)}'
                }), 400

        # Validate capacity if provided
        if 'capacity' in data:
            if not isinstance(data['capacity'], int) or data['capacity'] <= 0:
                return jsonify({'error': 'Capacity must be a positive integer'}), 400

        # Check if room name already exists (if changing name)
        if data.get('name') and data['name'] != room.name:
            existing_room = Room.query.filter_by(name=data['name']).first()
            if existing_room:
                return jsonify({'error': 'Room name already exists'}), 400

        # Update fields
        if 'name' in data:
            room.name = data['name']
        if 'room_type' in data:
            room.room_type = data['room_type']
        if 'capacity' in data:
            room.capacity = data['capacity']
        if 'is_available' in data:
            room.is_available = data['is_available']

        db.session.commit()

        return jsonify({
            'message': 'Room updated successfully',
            'room': {
                'id': room.id,
                'name': room.name,
                'room_type': room.room_type,
                'capacity': room.capacity,
                'is_available': room.is_available,
                'created_at': room.created_at.isoformat(),
                'updated_at': room.updated_at.isoformat()
            }
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Room name already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@rooms_bp.route('/<int:room_id>', methods=['DELETE'])
@token_required
def delete_room(current_admin, room_id):
    """Delete a room."""
    try:
        room = Room.query.get_or_404(room_id)

        # Check if room has timetable slots
        if room.timetable_slots:
            return jsonify({
                'error': 'Cannot delete room with scheduled classes. Please remove all schedules first.'
            }), 400

        db.session.delete(room)
        db.session.commit()

        return jsonify({'message': 'Room deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@rooms_bp.route('/<int:room_id>/schedule', methods=['GET'])
@token_required
def get_room_schedule(current_admin, room_id):
    """Get room's complete schedule."""
    try:
        room = Room.query.get_or_404(room_id)

        # Get query parameters for filtering
        timetable_id = request.args.get('timetable_id', type=int)

        # Build query for timetable slots
        from models.timetable import TimeTableSlot
        query = TimeTableSlot.query.filter_by(room_id=room_id)

        if timetable_id:
            query = query.filter_by(timetable_id=timetable_id)

        slots = query.order_by(
            TimeTableSlot.day_of_week,
            TimeTableSlot.start_time
        ).all()

        return jsonify({
            'room': {
                'id': room.id,
                'name': room.name,
                'room_type': room.room_type,
                'capacity': room.capacity
            },
            'schedule': [{
                'id': slot.id,
                'course_name': slot.course.name,
                'course_code': slot.course.code,
                'teacher_name': slot.course.teacher.name if slot.course.teacher else None,
                'day_of_week': slot.day_of_week,
                'day_name': slot.day_name,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'notes': slot.notes,
                'timetable_id': slot.timetable_id,
                'timetable_name': slot.timetable.name
            } for slot in slots]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rooms_bp.route('/availability', methods=['POST'])
@token_required
def check_room_availability(current_admin):
    """Check room availability for a specific time slot."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['day_of_week', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        from datetime import time
        from models.timetable import TimeTableSlot

        # Parse time strings
        try:
            start_time = time.fromisoformat(data['start_time'])
            end_time = time.fromisoformat(data['end_time'])
        except ValueError:
            return jsonify({'error': 'Invalid time format. Use HH:MM format.'}), 400

        # Build query for available rooms
        query = Room.query.filter_by(is_available=True)

        # Apply filters if provided
        if 'room_type' in data:
            query = query.filter_by(room_type=data['room_type'])

        if 'min_capacity' in data:
            query = query.filter(Room.capacity >= data['min_capacity'])

        all_rooms = query.all()

        # Check which rooms are available at the specified time
        available_rooms = []
        for room in all_rooms:
            # Check for conflicting slots
            conflicting_slots = TimeTableSlot.query.filter(
                TimeTableSlot.room_id == room.id,
                TimeTableSlot.day_of_week == data['day_of_week'],
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

        return jsonify({
            'available_rooms': available_rooms,
            'total_available': len(available_rooms)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500