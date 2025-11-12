from flask import Blueprint, request, jsonify
from models.timetable import TimeTable, TimeTableSlot
from models.department import Department
from config.db import db
from services.jwt_service import token_required
from datetime import datetime, date

timetables_bp = Blueprint('timetables', __name__, url_prefix='/api/timetables')


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


@timetables_bp.route('/', methods=['GET'])
def get_timetables():
    """Get all timetables with optional filtering."""
    try:
        # Get query parameters
        department_id = request.args.get('department_id', type=int)
        status = request.args.get('status')
        academic_year = request.args.get('academic_year')
        semester = request.args.get('semester')
        include_slots = request.args.get('include_slots', 'false').lower() == 'true'

        # Build query
        query = TimeTable.query

        if department_id:
            query = query.filter_by(department_id=department_id)

        if status:
            query = query.filter_by(status=status)

        if academic_year:
            query = query.filter_by(academic_year=academic_year)

        if semester:
            query = query.filter_by(semester=semester)

        timetables = query.order_by(TimeTable.created_at.desc()).all()

        return jsonify({
            'timetables': [serialize_timetable(tt, include_slots=True) for tt in timetables],
            'count': len(timetables)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/', methods=['POST'])
@token_required
def create_timetable(current_admin):
    """Create a new timetable."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'department_id', 'week_start']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Check if department exists
        department = Department.query.get(data['department_id'])
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        # Parse dates
        try:
            week_start = date.fromisoformat(data['week_start'])
            week_end = date.fromisoformat(data['week_end']) if data.get('week_end') else None
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD format.'}), 400

        # Validate week_end is after week_start
        if week_end and week_end <= week_start:
            return jsonify({'error': 'Week end must be after week start'}), 400

        # Validate status
        valid_statuses = ['draft', 'published', 'archived']
        status = data.get('status', 'draft')
        if status not in valid_statuses:
            return jsonify({
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400

        # Create new timetable
        timetable = TimeTable(
            name=data['name'],
            department_id=data['department_id'],
            week_start=week_start,
            week_end=week_end,
            academic_year=data.get('academic_year'),
            semester=data.get('semester'),
            status=status,
            created_by=current_admin.id
        )

        db.session.add(timetable)
        db.session.commit()

        return jsonify({
            'message': 'Timetable created successfully',
            'timetable': serialize_timetable(timetable, include_slots=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>', methods=['GET'])
def get_timetable(timetable_id):
    """Get a specific timetable with all its slots."""
    try:
        timetable = TimeTable.query.get_or_404(timetable_id)
        include_slots = request.args.get('include_slots', 'true').lower() == 'true'

        return jsonify({
            'timetable': serialize_timetable(timetable, include_slots=include_slots)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>', methods=['PUT'])
@token_required
def update_timetable(current_admin, timetable_id):
    """Update a timetable."""
    try:
        timetable = TimeTable.query.get_or_404(timetable_id)
        data = request.get_json()

        # Check if department exists (if changing department)
        if 'department_id' in data:
            department = Department.query.get(data['department_id'])
            if not department:
                return jsonify({'error': 'Department not found'}), 404

        # Parse dates if provided
        if 'week_start' in data:
            try:
                week_start = date.fromisoformat(data['week_start'])
            except ValueError:
                return jsonify({'error': 'Invalid week_start date format. Use YYYY-MM-DD format.'}), 400
        else:
            week_start = timetable.week_start

        if 'week_end' in data and data['week_end']:
            try:
                week_end = date.fromisoformat(data['week_end'])
            except ValueError:
                return jsonify({'error': 'Invalid week_end date format. Use YYYY-MM-DD format.'}), 400

            # Validate week_end is after week_start
            if week_end <= week_start:
                return jsonify({'error': 'Week end must be after week start'}), 400
        elif 'week_end' in data:
            week_end = None
        else:
            week_end = timetable.week_end

        # Validate status
        if 'status' in data:
            valid_statuses = ['draft', 'published', 'archived']
            if data['status'] not in valid_statuses:
                return jsonify({
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                }), 400

        # Update fields
        if 'name' in data:
            timetable.name = data['name']
        if 'department_id' in data:
            timetable.department_id = data['department_id']
        if 'week_start' in data:
            timetable.week_start = week_start
        if 'week_end' in data:
            timetable.week_end = week_end
        if 'academic_year' in data:
            timetable.academic_year = data['academic_year']
        if 'semester' in data:
            timetable.semester = data['semester']
        if 'status' in data:
            timetable.status = data['status']

        db.session.commit()

        include_slots = request.args.get('include_slots', 'true').lower() == 'true'

        return jsonify({
            'message': 'Timetable updated successfully',
            'timetable': serialize_timetable(timetable, include_slots=include_slots)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>', methods=['DELETE'])
@token_required
def delete_timetable(current_admin, timetable_id):
    """Delete a timetable and all its slots."""
    try:
        timetable = TimeTable.query.get_or_404(timetable_id)
        timetable_name = timetable.name
        slots_count = len(timetable.slots)

        # The slots will be automatically deleted due to cascade='all, delete-orphan'
        db.session.delete(timetable)
        db.session.commit()

        return jsonify({
            'message': 'Timetable deleted successfully',
            'deleted_timetable': {
                'name': timetable_name,
                'slots_deleted': slots_count
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>/publish', methods=['PUT'])
@token_required
def publish_timetable(current_admin, timetable_id):
    """Publish a timetable (change status to published)."""
    try:
        timetable = TimeTable.query.get_or_404(timetable_id)

        if timetable.status == 'published':
            return jsonify({'error': 'Timetable is already published'}), 400

        timetable.status = 'published'
        db.session.commit()

        return jsonify({
            'message': 'Timetable published successfully',
            'timetable': serialize_timetable(timetable, include_slots=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>/archive', methods=['PUT'])
@token_required
def archive_timetable(current_admin, timetable_id):
    """Archive a timetable (change status to archived)."""
    try:
        timetable = TimeTable.query.get_or_404(timetable_id)

        if timetable.status == 'archived':
            return jsonify({'error': 'Timetable is already archived'}), 400

        timetable.status = 'archived'
        db.session.commit()

        return jsonify({
            'message': 'Timetable archived successfully',
            'timetable': serialize_timetable(timetable, include_slots=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>/clone', methods=['POST'])
@token_required
def clone_timetable(current_admin, timetable_id):
    """Create a copy of an existing timetable."""
    try:
        original = TimeTable.query.get_or_404(timetable_id)
        data = request.get_json()

        # Validate required fields for clone
        if not data.get('name'):
            return jsonify({'error': 'name is required for cloned timetable'}), 400

        # Parse new dates if provided
        week_start = original.week_start
        week_end = original.week_end

        if data.get('week_start'):
            try:
                week_start = date.fromisoformat(data['week_start'])
            except ValueError:
                return jsonify({'error': 'Invalid week_start date format. Use YYYY-MM-DD format.'}), 400

        if data.get('week_end'):
            try:
                week_end = date.fromisoformat(data['week_end'])
            except ValueError:
                return jsonify({'error': 'Invalid week_end date format. Use YYYY-MM-DD format.'}), 400

        # Create new timetable
        new_timetable = TimeTable(
            name=data['name'],
            department_id=data.get('department_id', original.department_id),
            week_start=week_start,
            week_end=week_end,
            academic_year=data.get('academic_year', original.academic_year),
            semester=data.get('semester', original.semester),
            status='draft',
            created_by=current_admin.id
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

        return jsonify({
            'message': 'Timetable cloned successfully',
            'original_id': original.id,
            'timetable': serialize_timetable(new_timetable, include_slots=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>/stats', methods=['GET'])
def get_timetable_stats(timetable_id):
    """Get statistics for a specific timetable."""
    try:
        timetable = TimeTable.query.get_or_404(timetable_id)

        # Calculate statistics
        total_slots = len(timetable.slots)
        unique_courses = len(set(slot.course_id for slot in timetable.slots))
        unique_rooms = len(set(slot.room_id for slot in timetable.slots))
        unique_teachers = len(set(slot.course.teacher_id for slot in timetable.slots if slot.course and slot.course.teacher_id))

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

        return jsonify({
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
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500