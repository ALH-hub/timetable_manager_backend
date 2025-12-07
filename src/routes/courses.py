from flask import Blueprint, request, jsonify
from services.course_service import (
    get_all_courses,
    get_course_by_id,
    create_course,
    update_course,
    delete_course,
    assign_teacher_to_course,
    unassign_teacher_from_course,
    serialize_course
)
from services.jwt_service import token_required

courses_bp = Blueprint('courses', __name__, url_prefix='/api/courses')


@courses_bp.route('/', methods=['GET'])
@token_required
def get_courses(current_admin):
    """Get all courses with optional filtering."""
    try:
        department_id = request.args.get('department_id', type=int)
        teacher_id = request.args.get('teacher_id', type=int)
        level_id = request.args.get('level_id', type=int)
        semester = request.args.get('semester')
        year = request.args.get('year', type=int)
        is_active = request.args.get('is_active', type=bool)

        courses = get_all_courses(
            department_id=department_id,
            teacher_id=teacher_id,
            level_id=level_id,
            semester=semester,
            year=year,
            is_active=is_active
        ).all()

        return jsonify({
            'courses': [serialize_course(course) for course in courses]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/', methods=['POST'])
@token_required
def create_course_route(current_admin):
    """Create a new course."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'code', 'department_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        course, error = create_course(
            name=data['name'],
            code=data['code'],
            department_id=data['department_id'],
            teacher_id=data.get('teacher_id'),
            level_id=data.get('level_id'),
            weekly_sessions=data.get('weekly_sessions', 1),
            semester=data.get('semester'),
            year=data.get('year'),
            is_active=data.get('is_active', True)
        )

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Course created successfully',
            'course': serialize_course(course)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/<int:course_id>', methods=['GET'])
@token_required
def get_course(current_admin, course_id):
    """Get a specific course."""
    try:
        course = get_course_by_id(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        return jsonify({
            'course': serialize_course(course, include_schedule=True)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/<int:course_id>', methods=['PUT'])
@token_required
def update_course_route(current_admin, course_id):
    """Update a course."""
    try:
        data = request.get_json()

        # Build update dictionary
        update_data = {}
        allowed_fields = ['name', 'code', 'department_id', 'teacher_id', 'level_id',
                         'weekly_sessions', 'semester', 'year', 'is_active']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400

        course, error = update_course(course_id, **update_data)

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Course updated successfully',
            'course': serialize_course(course)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@token_required
def delete_course_route(current_admin, course_id):
    """Delete a course."""
    try:
        success, error = delete_course(course_id)

        if not success:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({'message': 'Course deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/<int:course_id>/assign-teacher', methods=['PUT'])
@token_required
def assign_teacher_route(current_admin, course_id):
    """Assign a teacher to a course."""
    try:
        data = request.get_json()

        if not data.get('teacher_id'):
            return jsonify({'error': 'teacher_id is required'}), 400

        course, error = assign_teacher_to_course(course_id, data['teacher_id'])

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Teacher assigned successfully',
            'course': {
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'teacher_id': course.teacher_id,
                'teacher_name': course.teacher.name if course.teacher else None,
                'level_id': course.level_id,
                'level_name': course.level.name if course.level else None
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/<int:course_id>/unassign-teacher', methods=['PUT'])
@token_required
def unassign_teacher_route(current_admin, course_id):
    """Unassign teacher from a course."""
    try:
        course, error = unassign_teacher_from_course(course_id)

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Teacher unassigned successfully',
            'course': {
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'teacher_id': None,
                'teacher_name': None,
                'level_id': course.level_id,
                'level_name': course.level.name if course.level else None
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
