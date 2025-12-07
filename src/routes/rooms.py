from flask import Blueprint, request, jsonify
from services.room_service import (
    get_all_rooms,
    get_room_by_id,
    create_room,
    update_room,
    delete_room,
    get_room_schedule,
    check_room_availability,
    serialize_room
)
from services.jwt_service import token_required

rooms_bp = Blueprint('rooms', __name__, url_prefix='/api/rooms')


@rooms_bp.route('/', methods=['GET'])
@token_required
def get_rooms(current_admin):
    """Get all rooms with optional filtering."""
    try:
        room_type = request.args.get('room_type')
        is_available = request.args.get('is_available', type=bool)
        min_capacity = request.args.get('min_capacity', type=int)
        max_capacity = request.args.get('max_capacity', type=int)

        rooms = get_all_rooms(
            room_type=room_type,
            is_available=is_available,
            min_capacity=min_capacity,
            max_capacity=max_capacity
        ).all()

        return jsonify({
            'rooms': [serialize_room(room) for room in rooms]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rooms_bp.route('/', methods=['POST'])
@token_required
def create_room_route(current_admin):
    """Create a new room."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'room_type', 'capacity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        room, error = create_room(
            name=data['name'],
            room_type=data['room_type'],
            capacity=data['capacity'],
            is_available=data.get('is_available', True)
        )

        if error:
            return jsonify({'error': error}), 400

        return jsonify({
            'message': 'Room created successfully',
            'room': serialize_room(room)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rooms_bp.route('/<int:room_id>', methods=['GET'])
@token_required
def get_room(current_admin, room_id):
    """Get a specific room."""
    try:
        room = get_room_by_id(room_id)
        if not room:
            return jsonify({'error': 'Room not found'}), 404

        return jsonify({
            'room': serialize_room(room, include_schedule=True)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rooms_bp.route('/<int:room_id>', methods=['PUT'])
@token_required
def update_room_route(current_admin, room_id):
    """Update a room."""
    try:
        data = request.get_json()

        # Build update dictionary
        update_data = {}
        allowed_fields = ['name', 'room_type', 'capacity', 'is_available']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400

        room, error = update_room(room_id, **update_data)

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Room updated successfully',
            'room': serialize_room(room)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rooms_bp.route('/<int:room_id>', methods=['DELETE'])
@token_required
def delete_room_route(current_admin, room_id):
    """Delete a room."""
    try:
        success, error = delete_room(room_id)

        if not success:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({'message': 'Room deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rooms_bp.route('/<int:room_id>/schedule', methods=['GET'])
@token_required
def get_room_schedule_route(current_admin, room_id):
    """Get room's complete schedule."""
    try:
        room = get_room_by_id(room_id)
        if not room:
            return jsonify({'error': 'Room not found'}), 404

        timetable_id = request.args.get('timetable_id', type=int)
        slots = get_room_schedule(room_id, timetable_id)

        from services.slot_service import serialize_slot
        return jsonify({
            'room': {
                'id': room.id,
                'name': room.name,
                'room_type': room.room_type,
                'capacity': room.capacity
            },
            'schedule': [serialize_slot(slot) for slot in slots]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rooms_bp.route('/availability', methods=['POST'])
@token_required
def check_room_availability_route(current_admin):
    """Check room availability for a specific time slot."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['day_of_week', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        available_rooms, error = check_room_availability(
            day_of_week=data['day_of_week'],
            start_time_str=data['start_time'],
            end_time_str=data['end_time'],
            room_type=data.get('room_type'),
            min_capacity=data.get('min_capacity')
        )

        if error:
            return jsonify({'error': error}), 400

        return jsonify({
            'available_rooms': available_rooms,
            'total_available': len(available_rooms)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
