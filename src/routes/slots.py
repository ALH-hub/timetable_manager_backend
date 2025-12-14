from flask import Blueprint, request, jsonify
from services.slot_service import (
    get_all_slots,
    get_slot_by_id,
    create_slot,
    update_slot,
    delete_slot,
    check_conflicts,
    bulk_create_slots,
    serialize_slot
)
from services.jwt_service import token_required

slots_bp = Blueprint('slots', __name__, url_prefix='/api/timetables/<int:timetable_id>/slots')


@slots_bp.route('/', methods=['GET'])
def get_slots(timetable_id):
    """Get all timetable slots with optional filtering."""
    try:
        course_id = request.args.get('course_id', type=int)
        room_id = request.args.get('room_id', type=int)
        day_of_week = request.args.get('day_of_week', type=int)

        slots = get_all_slots(
            timetable_id=timetable_id,
            course_id=course_id,
            room_id=room_id,
            day_of_week=day_of_week
        ).all()

        return jsonify({
            'slots': [serialize_slot(slot) for slot in slots]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@slots_bp.route('/', methods=['POST'])
@token_required
def create_slot_route(current_admin, timetable_id):
    """Create a new timetable slot."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['course_id', 'room_id', 'day_of_week', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        slot, error = create_slot(
            timetable_id=timetable_id,
            course_id=data['course_id'],
            room_id=data['room_id'],
            day_of_week=data['day_of_week'],
            start_time_str=data['start_time'],
            end_time_str=data['end_time'],
            notes=data.get('notes')
        )

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Timetable slot created successfully',
            'slot': serialize_slot(slot)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@slots_bp.route('/<int:slot_id>', methods=['GET'])
def get_slot(timetable_id, slot_id):
    """Get a specific timetable slot."""
    try:
        slot = get_slot_by_id(slot_id)
        if not slot:
            return jsonify({'error': 'Timetable slot not found'}), 404

        if slot.timetable_id != timetable_id:
            return jsonify({'error': 'Timetable slot not found'}), 404

        slot_data = serialize_slot(slot)
        slot_data['timetable_status'] = slot.timetable.status if slot.timetable else None
        slot_data['teacher_id'] = slot.course.teacher_id if slot.course else None
        slot_data['teacher_email'] = slot.course.teacher.email if slot.course and slot.course.teacher else None
        slot_data['room_type'] = slot.room.room_type if slot.room else None
        slot_data['room_capacity'] = slot.room.capacity if slot.room else None

        return jsonify({
            'slot': slot_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@slots_bp.route('/<int:slot_id>', methods=['PUT'])
@token_required
def update_slot_route(current_admin, timetable_id, slot_id):
    """Update a timetable slot."""
    try:
        slot = get_slot_by_id(slot_id)
        if not slot or slot.timetable_id != timetable_id:
            return jsonify({'error': 'Timetable slot not found'}), 404

        data = request.get_json()

        # Build update dictionary
        update_data = {}
        if 'timetable_id' in data:
            update_data['timetable_id'] = timetable_id
        if 'course_id' in data:
            update_data['course_id'] = data['course_id']
        if 'room_id' in data:
            update_data['room_id'] = data['room_id']
        if 'day_of_week' in data:
            update_data['day_of_week'] = data['day_of_week']
        if 'start_time' in data:
            update_data['start_time_str'] = data['start_time']
        if 'end_time' in data:
            update_data['end_time_str'] = data['end_time']
        if 'notes' in data:
            update_data['notes'] = data['notes']

        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400

        slot, error = update_slot(slot_id, **update_data)

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Timetable slot updated successfully',
            'slot': serialize_slot(slot)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@slots_bp.route('/<int:slot_id>', methods=['DELETE'])
@token_required
def delete_slot_route(current_admin, timetable_id, slot_id):
    """Delete a timetable slot."""
    try:
        slot = get_slot_by_id(slot_id)
        if not slot or slot.timetable_id != timetable_id:
            return jsonify({'error': 'Wrong timetable slot for this timetable'}), 404

        success, error = delete_slot(slot_id)

        if not success:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({'message': 'Timetable slot deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@slots_bp.route('/conflicts', methods=['POST'])
@token_required
def check_conflicts_route(current_admin, timetable_id):
    """Check for scheduling conflicts for a proposed time slot."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['course_id', 'day_of_week', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Room ID is optional for conflict checking
        room_id = data.get('room_id')
        exclude_slot_id = data.get('exclude_slot_id')

        conflicts, error = check_conflicts(
            course_id=data['course_id'],
            room_id=room_id,
            day_of_week=data['day_of_week'],
            start_time_str=data['start_time'],
            end_time_str=data['end_time'],
            timetable_id=timetable_id,
            exclude_slot_id=exclude_slot_id
        )

        if error:
            return jsonify({'error': error}), 400

        return jsonify({
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@slots_bp.route('/bulk-create', methods=['POST'])
@token_required
def bulk_create_slots_route(current_admin, timetable_id):
    """Create multiple timetable slots at once."""
    try:
        data = request.get_json()

        if not data.get('slots') or not isinstance(data['slots'], list):
            return jsonify({'error': 'slots array is required'}), 400

        created_slots, errors = bulk_create_slots(timetable_id, data['slots'])

        if errors:
            return jsonify({
                'error': 'Bulk creation failed',
                'errors': errors,
                'created_count': len(created_slots)
            }), 400

        return jsonify({
            'message': f'{len(created_slots)} slots created successfully',
            'created_count': len(created_slots),
            'slots': [{
                'id': slot.id,
                'course_name': slot.course.name if slot.course else None,
                'room_name': slot.room.name if slot.room else None,
                'day_name': slot.day_name,
                'start_time': slot.start_time.strftime('%H:%M') if slot.start_time else None,
                'end_time': slot.end_time.strftime('%H:%M') if slot.end_time else None
            } for slot in created_slots]
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
