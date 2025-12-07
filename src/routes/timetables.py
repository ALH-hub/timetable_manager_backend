from flask import Blueprint, request, jsonify
from services.timetable_service import (
    get_all_timetables,
    get_timetable_by_id,
    create_timetable,
    update_timetable,
    delete_timetable,
    publish_timetable,
    archive_timetable,
    clone_timetable,
    get_timetable_stats,
    serialize_timetable
)
from services.jwt_service import token_required

timetables_bp = Blueprint('timetables', __name__, url_prefix='/api/timetables')


@timetables_bp.route('/', methods=['GET'])
def get_timetables():
    """Get all timetables with optional filtering."""
    try:
        department_id = request.args.get('department_id', type=int)
        status = request.args.get('status')
        academic_year = request.args.get('academic_year')
        semester = request.args.get('semester')
        include_slots = request.args.get('include_slots', 'true').lower() == 'true'

        timetables = get_all_timetables(
            department_id=department_id,
            status=status,
            academic_year=academic_year,
            semester=semester
        ).all()

        return jsonify({
            'timetables': [serialize_timetable(tt, include_slots) for tt in timetables],
            'count': len(timetables)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/', methods=['POST'])
@token_required
def create_timetable_route(current_admin):
    """Create a new timetable."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'department_id', 'week_start']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        timetable, error = create_timetable(
            name=data['name'],
            department_id=data['department_id'],
            week_start=data['week_start'],
            week_end=data.get('week_end'),
            academic_year=data.get('academic_year'),
            semester=data.get('semester'),
            status=data.get('status', 'draft'),
            created_by=current_admin.id
        )

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Timetable created successfully',
            'timetable': serialize_timetable(timetable, include_slots=True)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>', methods=['GET'])
def get_timetable(timetable_id):
    """Get a specific timetable with all its slots."""
    try:
        timetable = get_timetable_by_id(timetable_id)
        if not timetable:
            return jsonify({'error': 'Timetable not found'}), 404

        include_slots = request.args.get('include_slots', 'true').lower() == 'true'

        return jsonify({
            'timetable': serialize_timetable(timetable, include_slots=include_slots)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>', methods=['PUT'])
@token_required
def update_timetable_route(current_admin, timetable_id):
    """Update a timetable."""
    try:
        data = request.get_json()

        # Build update dictionary
        update_data = {}
        allowed_fields = ['name', 'department_id', 'week_start', 'week_end',
                         'academic_year', 'semester', 'status']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400

        timetable, error = update_timetable(timetable_id, **update_data)

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        include_slots = request.args.get('include_slots', 'true').lower() == 'true'

        return jsonify({
            'message': 'Timetable updated successfully',
            'timetable': serialize_timetable(timetable, include_slots=include_slots)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>', methods=['DELETE'])
@token_required
def delete_timetable_route(current_admin, timetable_id):
    """Delete a timetable and all its slots."""
    try:
        success, error, deleted_info = delete_timetable(timetable_id)

        if not success:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Timetable deleted successfully',
            'deleted_timetable': deleted_info
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>/publish', methods=['PUT'])
@token_required
def publish_timetable_route(current_admin, timetable_id):
    """Publish a timetable (change status to published)."""
    try:
        timetable, error = publish_timetable(timetable_id)

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Timetable published successfully',
            'timetable': serialize_timetable(timetable, include_slots=True)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>/archive', methods=['PUT'])
@token_required
def archive_timetable_route(current_admin, timetable_id):
    """Archive a timetable (change status to archived)."""
    try:
        timetable, error = archive_timetable(timetable_id)

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Timetable archived successfully',
            'timetable': serialize_timetable(timetable, include_slots=True)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>/clone', methods=['POST'])
@token_required
def clone_timetable_route(current_admin, timetable_id):
    """Create a copy of an existing timetable."""
    try:
        data = request.get_json()

        if not data.get('name'):
            return jsonify({'error': 'name is required for cloned timetable'}), 400

        new_timetable, error = clone_timetable(
            timetable_id=timetable_id,
            name=data['name'],
            week_start=data.get('week_start'),
            week_end=data.get('week_end'),
            department_id=data.get('department_id'),
            academic_year=data.get('academic_year'),
            semester=data.get('semester'),
            created_by=current_admin.id
        )

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Timetable cloned successfully',
            'original_id': timetable_id,
            'timetable': serialize_timetable(new_timetable, include_slots=True)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timetables_bp.route('/<int:timetable_id>/stats', methods=['GET'])
def get_timetable_stats_route(timetable_id):
    """Get statistics for a specific timetable."""
    try:
        stats = get_timetable_stats(timetable_id)

        if not stats:
            return jsonify({'error': 'Timetable not found'}), 404

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
