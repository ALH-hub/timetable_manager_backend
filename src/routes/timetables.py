from flask import Blueprint, request, jsonify
from models.timetable import TimeTable
from models.department import Department
from config.db import db
from services.jwt_service import token_required
from datetime import datetime, date

timetables_bp = Blueprint('timetables', __name__, url_prefix='/api/timetables')


@timetables_bp.route('/', methods=['GET'])
def get_timetables():
    """Get all timetables with optional filtering."""
    try:
        # Get query parameters
        department_id = request.args.get('department_id', type=int)
        status = request.args.get('status')
        academic_year = request.args.get('academic_year')
        semester = request.args.get('semester')

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
            'timetables': [{
                'id': timetable.id,
                'name': timetable.name,
                'department_id': timetable.department_id,
                'department_name': timetable.department.name,
                'week_start': timetable.week_start.isoformat() if timetable.week_start else None,
                'week_end': timetable.week_end.isoformat() if timetable.week_end else None,
                'academic_year': timetable.academic_year,
                'semester': timetable.semester,
                'status': timetable.status,
                'created_by': timetable.created_by,
                'creator_name': timetable.creator.username if timetable.creator else None,
                'created_at': timetable.created_at.isoformat(),
                'updated_at': timetable.updated_at.isoformat(),
                'slots_count': len(timetable.slots)
            } for timetable in timetables]
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
            'timetable': {
                'id': timetable.id,
                'name': timetable.name,
                'department_id': timetable.department_id,
                'department_name': timetable.department.name,
                'week_start': timetable.week_start.isoformat(),
                'week_end': timetable.week_end.isoformat() if timetable.week_end else None,
                'academic_year': timetable.academic_year,
                'semester': timetable.semester,
                'status': timetable.status,
                'created_by': timetable.created_by,
                'creator_name': current_admin.username,
                'created_at': timetable.created_at.isoformat(),
                'updated_at': timetable.updated_at.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>', methods=['GET'])
@token_required
def get_timetable(current_admin, timetable_id):
    """Get a specific timetable with all its slots."""
    try:
        timetable = TimeTable.query.get_or_404(timetable_id)

        # Get slots ordered by day and time
        slots = sorted(timetable.slots, key=lambda x: (x.day_of_week, x.start_time))

        return jsonify({
            'timetable': {
                'id': timetable.id,
                'name': timetable.name,
                'department_id': timetable.department_id,
                'department_name': timetable.department.name,
                'week_start': timetable.week_start.isoformat(),
                'week_end': timetable.week_end.isoformat() if timetable.week_end else None,
                'academic_year': timetable.academic_year,
                'semester': timetable.semester,
                'status': timetable.status,
                'created_by': timetable.created_by,
                'creator_name': timetable.creator.username if timetable.creator else None,
                'created_at': timetable.created_at.isoformat(),
                'updated_at': timetable.updated_at.isoformat(),
                'slots': [{
                    'id': slot.id,
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
            }
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

        return jsonify({
            'message': 'Timetable updated successfully',
            'timetable': {
                'id': timetable.id,
                'name': timetable.name,
                'department_id': timetable.department_id,
                'department_name': timetable.department.name,
                'week_start': timetable.week_start.isoformat(),
                'week_end': timetable.week_end.isoformat() if timetable.week_end else None,
                'academic_year': timetable.academic_year,
                'semester': timetable.semester,
                'status': timetable.status,
                'created_by': timetable.created_by,
                'creator_name': timetable.creator.username if timetable.creator else None,
                'created_at': timetable.created_at.isoformat(),
                'updated_at': timetable.updated_at.isoformat()
            }
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

        # The slots will be automatically deleted due to cascade='all, delete-orphan'
        db.session.delete(timetable)
        db.session.commit()

        return jsonify({'message': 'Timetable deleted successfully'}), 200

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
            'timetable': {
                'id': timetable.id,
                'name': timetable.name,
                'status': timetable.status,
                'updated_at': timetable.updated_at.isoformat()
            }
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
            'timetable': {
                'id': timetable.id,
                'name': timetable.name,
                'status': timetable.status,
                'updated_at': timetable.updated_at.isoformat()
            }
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
            status='draft',  # Always start as draft
            created_by=current_admin.id
        )

        db.session.add(new_timetable)
        db.session.flush()  # To get the new ID

        # Clone all slots
        from models.timetable import TimeTableSlot
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
            'timetable': {
                'id': new_timetable.id,
                'name': new_timetable.name,
                'department_id': new_timetable.department_id,
                'department_name': new_timetable.department.name,
                'week_start': new_timetable.week_start.isoformat(),
                'week_end': new_timetable.week_end.isoformat() if new_timetable.week_end else None,
                'academic_year': new_timetable.academic_year,
                'semester': new_timetable.semester,
                'status': new_timetable.status,
                'created_by': new_timetable.created_by,
                'creator_name': current_admin.username,
                'created_at': new_timetable.created_at.isoformat(),
                'slots_count': len(new_timetable.slots)
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500