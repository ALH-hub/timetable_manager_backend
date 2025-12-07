from flask import Blueprint, request, jsonify
from services.teacher_service import (
    get_all_teachers,
    get_teacher_by_id,
    create_teacher,
    update_teacher,
    delete_teacher,
    serialize_teacher
)
from services.jwt_service import token_required

teachers_bp = Blueprint('teachers', __name__, url_prefix='/api/teachers')


@teachers_bp.route('/', methods=['GET'])
@token_required
def get_teachers(current_admin):
    """Get all teachers with optional filtering."""
    try:
        department_id = request.args.get('department_id', type=int)
        is_active = request.args.get('is_active', type=bool)

        teachers = get_all_teachers(department_id=department_id, is_active=is_active).all()

        return jsonify({
            'teachers': [serialize_teacher(teacher) for teacher in teachers]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@teachers_bp.route('/', methods=['POST'])
@token_required
def create_teacher_route(current_admin):
    """Create a new teacher."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'email', 'department_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        teacher, error = create_teacher(
            name=data['name'],
            email=data['email'],
            department_id=data['department_id'],
            phone=data.get('phone'),
            specialization=data.get('specialization'),
            is_active=data.get('is_active', True)
        )

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Teacher created successfully',
            'teacher': serialize_teacher(teacher)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@teachers_bp.route('/<int:teacher_id>', methods=['GET'])
@token_required
def get_teacher(current_admin, teacher_id):
    """Get a specific teacher."""
    try:
        teacher = get_teacher_by_id(teacher_id)
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404

        return jsonify({
            'teacher': serialize_teacher(teacher, include_courses=True)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@teachers_bp.route('/<int:teacher_id>', methods=['PUT'])
@token_required
def update_teacher_route(current_admin, teacher_id):
    """Update a teacher."""
    try:
        data = request.get_json()

        # Build update dictionary
        update_data = {}
        allowed_fields = ['name', 'email', 'phone', 'department_id', 'specialization', 'is_active']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400

        teacher, error = update_teacher(teacher_id, **update_data)

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Teacher updated successfully',
            'teacher': serialize_teacher(teacher)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@teachers_bp.route('/<int:teacher_id>', methods=['DELETE'])
@token_required
def delete_teacher_route(current_admin, teacher_id):
    """Delete a teacher."""
    try:
        success, error = delete_teacher(teacher_id)

        if not success:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({'message': 'Teacher deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@teachers_bp.route('/<int:teacher_id>/courses', methods=['GET'])
@token_required
def get_teacher_courses(current_admin, teacher_id):
    """Get all courses taught by a teacher."""
    try:
        teacher = get_teacher_by_id(teacher_id)
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404

        from services.course_service import serialize_course
        return jsonify({
            'courses': [serialize_course(course) for course in teacher.courses]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@teachers_bp.route('/<int:teacher_id>/schedule', methods=['GET'])
@token_required
def get_teacher_schedule_route(current_admin, teacher_id):
    """Get teacher's timetable schedule."""
    try:
        teacher = get_teacher_by_id(teacher_id)
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404

        return jsonify({
            'schedule': serialize_teacher(teacher, include_schedule=True)['schedule']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
