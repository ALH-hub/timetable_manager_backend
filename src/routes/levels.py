from flask import Blueprint, request, jsonify
from models.level import Level
from services.level_service import (
    get_all_levels,
    get_level_by_id,
    get_level_by_code,
    create_level,
    update_level,
    delete_level,
    initialize_default_levels
)
from services.jwt_service import token_required
from sqlalchemy.exc import IntegrityError

levels_bp = Blueprint('levels', __name__, url_prefix='/api/levels')


@levels_bp.route('/', methods=['GET'])
@token_required
def get_levels(current_admin):
    """Get all levels with optional filtering."""
    try:
        # Get query parameters
        active_only = request.args.get('active_only', 'false').lower() == 'true'

        # Get levels
        levels_query = get_all_levels(active_only=active_only)
        levels = levels_query.all()

        return jsonify({
            'levels': [level.to_dict() for level in levels]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@levels_bp.route('/', methods=['POST'])
@token_required
def create_level_route(current_admin):
    """Create a new level."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Create level using service
        level, error = create_level(
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            order=data.get('order'),
            is_active=data.get('is_active', True)
        )

        if error:
            return jsonify({'error': error}), 400

        return jsonify({
            'message': 'Level created successfully',
            'level': level.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@levels_bp.route('/<int:level_id>', methods=['GET'])
@token_required
def get_level(current_admin, level_id):
    """Get a specific level."""
    try:
        level = get_level_by_id(level_id)
        if not level:
            return jsonify({'error': 'Level not found'}), 404

        return jsonify({
            'level': level.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@levels_bp.route('/<int:level_id>', methods=['PUT'])
@token_required
def update_level_route(current_admin, level_id):
    """Update a level."""
    try:
        data = request.get_json()

        # Build update dictionary
        update_data = {}
        allowed_fields = ['name', 'code', 'description', 'order', 'is_active']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400

        # Update level using service
        level, error = update_level(level_id, **update_data)

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Level updated successfully',
            'level': level.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@levels_bp.route('/<int:level_id>', methods=['DELETE'])
@token_required
def delete_level_route(current_admin, level_id):
    """Delete a level."""
    try:
        success, error = delete_level(level_id)

        if not success:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({'message': 'Level deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@levels_bp.route('/by-code/<code>', methods=['GET'])
@token_required
def get_level_by_code_route(current_admin, code):
    """Get a level by its code."""
    try:
        level = get_level_by_code(code)
        if not level:
            return jsonify({'error': 'Level not found'}), 404

        return jsonify({
            'level': level.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@levels_bp.route('/initialize', methods=['POST'])
@token_required
def initialize_levels(current_admin):
    """Initialize default levels (Level 1, 2, 3, Master 1, Master 2)."""
    try:
        created_levels = initialize_default_levels()

        return jsonify({
            'message': f'Initialized {len(created_levels)} default levels',
            'levels': [level.to_dict() for level in created_levels]
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@levels_bp.route('/<int:level_id>/courses', methods=['GET'])
@token_required
def get_level_courses(current_admin, level_id):
    """Get all courses for a specific level."""
    try:
        level = get_level_by_id(level_id)
        if not level:
            return jsonify({'error': 'Level not found'}), 404

        courses = level.courses.all()

        return jsonify({
            'level': {
                'id': level.id,
                'name': level.name,
                'code': level.code
            },
            'courses': [{
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'department_id': course.department_id,
                'department_name': course.department.name if course.department else None,
                'teacher_id': course.teacher_id,
                'teacher_name': course.teacher.name if course.teacher else None,
                'weekly_sessions': course.weekly_sessions,
                'semester': course.semester,
                'year': course.year,
                'is_active': course.is_active
            } for course in courses]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

