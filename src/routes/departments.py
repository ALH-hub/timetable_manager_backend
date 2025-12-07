from flask import Blueprint, request, jsonify
from services.department_service import (
    get_all_departments,
    get_department_by_id,
    create_department,
    update_department,
    delete_department,
    serialize_department
)
from services.course_service import serialize_course
from services.jwt_service import token_required

departments_bp = Blueprint('departments', __name__, url_prefix='/api/departments')


@departments_bp.route('/', methods=['GET'])
def get_departments():
    """Get all departments."""
    try:
        departments = get_all_departments().all()

        return jsonify({
            'departments': [serialize_department(dept) for dept in departments]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/', methods=['POST'])
@token_required
def create_department_route(current_admin):
    """Create a new department."""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Department name is required'}), 400

        department, error = create_department(
            name=data['name'],
            code=data.get('code'),
            head=data.get('head'),
            contact_email=data.get('contact_email')
        )

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Department created successfully',
            'department': serialize_department(department)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/<int:department_id>', methods=['GET'])
def get_department(department_id):
    """Get a specific department."""
    try:
        department = get_department_by_id(department_id)
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        return jsonify({
            'department': serialize_department(department, include_counts=True)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/<int:department_id>', methods=['PUT'])
@token_required
def update_department_route(current_admin, department_id):
    """Update a department."""
    try:
        data = request.get_json()

        # Build update dictionary
        update_data = {}
        allowed_fields = ['name', 'code', 'head', 'contact_email']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400

        department, error = update_department(department_id, **update_data)

        if error:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({
            'message': 'Department updated successfully',
            'department': serialize_department(department)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/<int:department_id>', methods=['DELETE'])
@token_required
def delete_department_route(current_admin, department_id):
    """Delete a department."""
    try:
        success, error = delete_department(department_id)

        if not success:
            status_code = 404 if 'not found' in error.lower() else 400
            return jsonify({'error': error}), status_code

        return jsonify({'message': 'Department deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/<int:department_id>/teachers', methods=['GET'])
@token_required
def get_department_teachers(current_admin, department_id):
    """Get all teachers in a department."""
    try:
        department = get_department_by_id(department_id)
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        from services.teacher_service import serialize_teacher
        return jsonify({
            'teachers': [serialize_teacher(teacher) for teacher in department.teachers]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/<int:department_id>/courses', methods=['GET'])
def get_department_courses(department_id):
    """Get all courses in a department."""
    try:
        department = get_department_by_id(department_id)
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        return jsonify({
            'courses': [serialize_course(course) for course in department.courses]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
