from flask import Blueprint, request, jsonify
from models.timetable import TimeTableSlot, TimeTable
from models.course import Course
from models.classroom import Room
from config.db import db
from services.jwt_service import token_required
from datetime import time

slots_bp = Blueprint('slots', __name__, url_prefix='/api/timetables/<int:timetable_id>/slots')


@slots_bp.route('/', methods=['GET'])
def get_slots(timetable_id):
    """Get all timetable slots with optional filtering."""
    try:
         # Get query parameters
        course_id = request.args.get('course_id', type=int)
        room_id = request.args.get('room_id', type=int)
        day_of_week = request.args.get('day_of_week', type=int)

        # Build query
        query = TimeTableSlot.query

        if timetable_id:
            query = query.filter_by(timetable_id=timetable_id)

        if course_id:
            query = query.filter_by(course_id=course_id)

        if room_id:
            query = query.filter_by(room_id=room_id)

        if day_of_week is not None:
            query = query.filter_by(day_of_week=day_of_week)

        slots = query.order_by(
            TimeTableSlot.day_of_week,
            TimeTableSlot.start_time
        ).all()

        return jsonify({
            'slots': [{
                'id': slot.id,
                'timetable_id': slot.timetable_id,
                'timetable_name': slot.timetable.name,
                'course_id': slot.course_id,
                'course_name': slot.course.name,
                'course_code': slot.course.code,
                'teacher_name': slot.course.teacher.name if slot.course.teacher else None,
                'room_id': slot.room_id,
                'room_name': slot.room.name,
                'day_of_week': slot.day_of_week,
                'day_name': slot.day_name,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'notes': slot.notes,
                'created_at': slot.created_at.isoformat(),
                'updated_at': slot.updated_at.isoformat()
            } for slot in slots]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@slots_bp.route('/', methods=['POST'])
@token_required
def create_slot(current_admin, timetable_id):
    """Create a new timetable slot."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['course_id', 'room_id', 'day_of_week', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Validate foreign keys exist
        timetable = TimeTable.query.get(timetable_id)
        if not timetable:
            return jsonify({'error': 'Timetable not found'}), 404

        course = Course.query.get(data['course_id'])
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        room = Room.query.get(data['room_id'])
        if not room:
            return jsonify({'error': 'Room not found'}), 404

        # Validate day_of_week
        if not isinstance(data['day_of_week'], int) or data['day_of_week'] < 0 or data['day_of_week'] > 6:
            return jsonify({'error': 'day_of_week must be an integer between 0 (Monday) and 6 (Sunday)'}), 400

        # Parse and validate times
        try:
            start_time = time.fromisoformat(data['start_time'])
            end_time = time.fromisoformat(data['end_time'])
        except ValueError:
            return jsonify({'error': 'Invalid time format. Use HH:MM format.'}), 400

        if start_time >= end_time:
            return jsonify({'error': 'Start time must be before end time'}), 400

        # Check if room is available
        if not room.is_available:
            return jsonify({'error': 'Room is not available'}), 400

        # Check for conflicts - room double booking
        room_conflict = TimeTableSlot.query.filter(
            TimeTableSlot.room_id == data['room_id'],
            TimeTableSlot.day_of_week == data['day_of_week'],
            TimeTableSlot.start_time < end_time,
            TimeTableSlot.end_time > start_time
        ).first()

        if room_conflict:
            return jsonify({
                'error': f'Room conflict: {room.name} is already booked at this time'
            }), 400

        # Check for teacher conflicts (if course has a teacher)
        if course.teacher_id:
            teacher_conflict = TimeTableSlot.query.join(Course).filter(
                Course.teacher_id == course.teacher_id,
                TimeTableSlot.day_of_week == data['day_of_week'],
                TimeTableSlot.start_time < end_time,
                TimeTableSlot.end_time > start_time
            ).first()

            if teacher_conflict:
                return jsonify({
                    'error': f'Teacher conflict: {course.teacher.name} is already scheduled at this time'
                }), 400

        # Create new slot
        slot = TimeTableSlot(
            timetable_id=timetable_id,
            course_id=data['course_id'],
            room_id=data['room_id'],
            day_of_week=data['day_of_week'],
            start_time=start_time,
            end_time=end_time,
            notes=data.get('notes')
        )

        db.session.add(slot)
        db.session.commit()

        return jsonify({
            'message': 'Timetable slot created successfully',
            'slot': {
                'id': slot.id,
                'timetable_id': slot.timetable_id,
                'timetable_name': slot.timetable.name,
                'course_id': slot.course_id,
                'course_name': slot.course.name,
                'course_code': slot.course.code,
                'teacher_name': slot.course.teacher.name if slot.course.teacher else None,
                'room_id': slot.room_id,
                'room_name': slot.room.name,
                'day_of_week': slot.day_of_week,
                'day_name': slot.day_name,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'notes': slot.notes,
                'created_at': slot.created_at.isoformat(),
                'updated_at': slot.updated_at.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@slots_bp.route('/<int:slot_id>', methods=['GET'])
def get_slot(timetable_id, slot_id):
    """Get a specific timetable slot."""
    try:
        slot = TimeTableSlot.query.get_or_404(slot_id)

        if slot.timetable_id != timetable_id :
            return jsonify({'error': 'Timetable slot not found!!'})

        return jsonify({
            'slot': {
                'id': slot.id,
                'timetable_id': slot.timetable_id,
                'timetable_name': slot.timetable.name,
                'timetable_status': slot.timetable.status,
                'course_id': slot.course_id,
                'course_name': slot.course.name,
                'course_code': slot.course.code,
                'teacher_id': slot.course.teacher_id,
                'teacher_name': slot.course.teacher.name if slot.course.teacher else None,
                'teacher_email': slot.course.teacher.email if slot.course.teacher else None,
                'room_id': slot.room_id,
                'room_name': slot.room.name,
                'room_type': slot.room.room_type,
                'room_capacity': slot.room.capacity,
                'day_of_week': slot.day_of_week,
                'day_name': slot.day_name,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'notes': slot.notes,
                'created_at': slot.created_at.isoformat(),
                'updated_at': slot.updated_at.isoformat()
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@slots_bp.route('/<int:slot_id>', methods=['PUT'])
@token_required
def update_slot(current_admin, timetable_id, slot_id):
    """Update a timetable slot."""
    try:
        slot = TimeTableSlot.query.get_or_404(slot_id)
        data = request.get_json()

        # Validate foreign keys if provided
        if timetable_id:
            timetable = TimeTable.query.get(timetable_id)
            if not timetable:
                return jsonify({'error': 'Timetable not found'}), 404

        if 'course_id' in data:
            course = Course.query.get(data['course_id'])
            if not course:
                return jsonify({'error': 'Course not found'}), 404

        if 'room_id' in data:
            room = Room.query.get(data['room_id'])
            if not room:
                return jsonify({'error': 'Room not found'}), 404

            # Check if room is available
            if not room.is_available:
                return jsonify({'error': 'Room is not available'}), 400

        # Validate day_of_week if provided
        if 'day_of_week' in data:
            if not isinstance(data['day_of_week'], int) or data['day_of_week'] < 0 or data['day_of_week'] > 6:
                return jsonify({'error': 'day_of_week must be an integer between 0 (Monday) and 6 (Sunday)'}), 400

        # Parse and validate times if provided
        start_time = slot.start_time
        end_time = slot.end_time

        if 'start_time' in data:
            try:
                start_time = time.fromisoformat(data['start_time'])
            except ValueError:
                return jsonify({'error': 'Invalid start_time format. Use HH:MM format.'}), 400

        if 'end_time' in data:
            try:
                end_time = time.fromisoformat(data['end_time'])
            except ValueError:
                return jsonify({'error': 'Invalid end_time format. Use HH:MM format.'}), 400

        if start_time >= end_time:
            return jsonify({'error': 'Start time must be before end time'}), 400

        # Check for conflicts if time/room/day is being changed
        room_id = data.get('room_id', slot.room_id)
        day_of_week = data.get('day_of_week', slot.day_of_week)

        if ('room_id' in data or 'day_of_week' in data or 'start_time' in data or 'end_time' in data):
            # Check for room conflicts (excluding current slot)
            room_conflict = TimeTableSlot.query.filter(
                TimeTableSlot.id != slot_id,
                TimeTableSlot.room_id == room_id,
                TimeTableSlot.day_of_week == day_of_week,
                TimeTableSlot.start_time < end_time,
                TimeTableSlot.end_time > start_time
            ).first()

            if room_conflict:
                room_obj = Room.query.get(room_id)
                return jsonify({
                    'error': f'Room conflict: {room_obj.name} is already booked at this time'
                }), 400

        # Check for teacher conflicts if course is being changed
        course_id = data.get('course_id', slot.course_id)
        if 'course_id' in data or 'day_of_week' in data or 'start_time' in data or 'end_time' in data:
            course_obj = Course.query.get(course_id)
            if course_obj and course_obj.teacher_id:
                teacher_conflict = TimeTableSlot.query.join(Course).filter(
                    TimeTableSlot.id != slot_id,
                    Course.teacher_id == course_obj.teacher_id,
                    TimeTableSlot.day_of_week == day_of_week,
                    TimeTableSlot.start_time < end_time,
                    TimeTableSlot.end_time > start_time
                ).first()

                if teacher_conflict:
                    return jsonify({
                        'error': f'Teacher conflict: {course_obj.teacher.name} is already scheduled at this time'
                    }), 400

        # Update fields
        if timetable_id:
            slot.timetable_id = timetable_id
        if 'course_id' in data:
            slot.course_id = data['course_id']
        if 'room_id' in data:
            slot.room_id = data['room_id']
        if 'day_of_week' in data:
            slot.day_of_week = data['day_of_week']
        if 'start_time' in data:
            slot.start_time = start_time
        if 'end_time' in data:
            slot.end_time = end_time
        if 'notes' in data:
            slot.notes = data['notes']

        db.session.commit()

        return jsonify({
            'message': 'Timetable slot updated successfully',
            'slot': {
                'id': slot.id,
                'timetable_id': slot.timetable_id,
                'timetable_name': slot.timetable.name,
                'course_id': slot.course_id,
                'course_name': slot.course.name,
                'course_code': slot.course.code,
                'teacher_name': slot.course.teacher.name if slot.course.teacher else None,
                'room_id': slot.room_id,
                'room_name': slot.room.name,
                'day_of_week': slot.day_of_week,
                'day_name': slot.day_name,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'notes': slot.notes,
                'created_at': slot.created_at.isoformat(),
                'updated_at': slot.updated_at.isoformat()
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@slots_bp.route('/<int:slot_id>', methods=['DELETE'])
@token_required
def delete_slot(current_admin, timetable_id, slot_id):
    """Delete a timetable slot."""
    try:
        slot = TimeTableSlot.query.get_or_404(slot_id)

        if slot.timetable_id != timetable_id:
            return jsonify({'error': 'Wrong timetable slot for this timetable'}), 404

        db.session.delete(slot)
        db.session.commit()

        return jsonify({'message': 'Timetable slot deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@slots_bp.route('/conflicts', methods=['POST'])
@token_required
def check_conflicts(current_admin, timetable_id):
    """Check for scheduling conflicts for a proposed time slot."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['course_id', 'room_id', 'day_of_week', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Parse times
        try:
            start_time = time.fromisoformat(data['start_time'])
            end_time = time.fromisoformat(data['end_time'])
        except ValueError:
            return jsonify({'error': 'Invalid time format. Use HH:MM format.'}), 400

        if start_time >= end_time:
            return jsonify({'error': 'Start time must be before end time'}), 400

        conflicts = []

        # Check room conflicts
        room_conflicts = TimeTableSlot.query.filter(
            TimeTableSlot.room_id == data['room_id'],
            TimeTableSlot.day_of_week == data['day_of_week'],
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
        course = Course.query.get(data['course_id'])
        if course and course.teacher_id:
            teacher_conflicts = TimeTableSlot.query.join(Course).filter(
                Course.teacher_id == course.teacher_id,
                TimeTableSlot.day_of_week == data['day_of_week'],
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

        return jsonify({
            'has_conflicts': len(conflicts) > 0,
            'conflicts': conflicts
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@slots_bp.route('/bulk-create', methods=['POST'])
@token_required
def bulk_create_slots(current_admin, timetable_id):
    """Create multiple timetable slots at once."""
    try:
        data = request.get_json()

        if not data.get('slots') or not isinstance(data['slots'], list):
            return jsonify({'error': 'slots array is required'}), 400

        created_slots = []
        errors = []

        for i, slot_data in enumerate(data['slots']):
            try:
                # Validate required fields for each slot
                required_fields = ['course_id', 'room_id', 'day_of_week', 'start_time', 'end_time']
                for field in required_fields:
                    if field not in slot_data:
                        errors.append(f'Slot {i+1}: {field} is required')
                        continue

                if errors:
                    continue

                # Parse times
                start_time = time.fromisoformat(slot_data['start_time'])
                end_time = time.fromisoformat(slot_data['end_time'])

                if start_time >= end_time:
                    errors.append(f'Slot {i+1}: Start time must be before end time')
                    continue

                # Check for conflicts
                room_conflict = TimeTableSlot.query.filter(
                    TimeTableSlot.room_id == slot_data['room_id'],
                    TimeTableSlot.day_of_week == slot_data['day_of_week'],
                    TimeTableSlot.start_time < end_time,
                    TimeTableSlot.end_time > start_time
                ).first()

                if room_conflict:
                    errors.append(f'Slot {i+1}: Room conflict detected')
                    continue

                # Create slot
                slot = TimeTableSlot(
                    timetable_id=timetable_id,
                    course_id=slot_data['course_id'],
                    room_id=slot_data['room_id'],
                    day_of_week=slot_data['day_of_week'],
                    start_time=start_time,
                    end_time=end_time,
                    notes=slot_data.get('notes')
                )

                db.session.add(slot)
                created_slots.append(slot)

            except Exception as e:
                errors.append(f'Slot {i+1}: {str(e)}')

        if errors:
            db.session.rollback()
            return jsonify({
                'error': 'Bulk creation failed',
                'errors': errors
            }), 400

        db.session.commit()

        return jsonify({
            'message': f'{len(created_slots)} slots created successfully',
            'created_count': len(created_slots),
            'slots': [{
                'id': slot.id,
                'course_name': slot.course.name,
                'room_name': slot.room.name,
                'day_name': slot.day_name,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M')
            } for slot in created_slots]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500