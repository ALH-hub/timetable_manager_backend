from flask import Blueprint, request, jsonify
from models.department import Department
from config.db import db
from services.jwt_service import token_required
from sqlalchemy.exc import IntegrityError

departments_bp = Blueprint('departments', __name__, url_prefix='/api/departments')


@departments_bp.route('/', methods=['GET'])
@token_required
def get_departments(current_admin):
    """Get all departments."""
    try:
        departments = Department.query.all()

        return jsonify({
            'departments': [{
                'id': dept.id,
                'name': dept.name,
                'code': dept.code,
                'head': dept.head,
                'contact_email': dept.contact_email,
                'created_at': dept.created_at.isoformat(),
                'updated_at': dept.updated_at.isoformat()
            } for dept in departments]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/', methods=['POST'])
@token_required
def create_department(current_admin):
    """Create a new department."""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Department name is required'}), 400

        # Check if department code already exists
        if data.get('code'):
            existing_dept = Department.query.filter_by(code=data['code']).first()
            if existing_dept:
                return jsonify({'error': 'Department code already exists'}), 400

        # Create new department
        department = Department(
            name=data['name'],
            code=data.get('code'),
            head=data.get('head'),
            contact_email=data.get('contact_email')
        )

        db.session.add(department)
        db.session.commit()

        return jsonify({
            'message': 'Department created successfully',
            'department': {
                'id': department.id,
                'name': department.name,
                'code': department.code,
                'head': department.head,
                'contact_email': department.contact_email,
                'created_at': department.created_at.isoformat(),
                'updated_at': department.updated_at.isoformat()
            }
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Department code already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/<int:department_id>', methods=['GET'])
@token_required
def get_department(current_admin, department_id):
    """Get a specific department."""
    try:
        department = Department.query.get_or_404(department_id)

        return jsonify({
            'department': {
                'id': department.id,
                'name': department.name,
                'code': department.code,
                'head': department.head,
                'contact_email': department.contact_email,
                'created_at': department.created_at.isoformat(),
                'updated_at': department.updated_at.isoformat(),
                'teachers_count': len(department.teachers),
                'courses_count': len(department.courses),
                'timetables_count': len(department.timetables)
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/<int:department_id>', methods=['PUT'])
@token_required
def update_department(current_admin, department_id):
    """Update a department."""
    try:
        department = Department.query.get_or_404(department_id)
        data = request.get_json()

        # Check if department code already exists (if changing code)
        if data.get('code') and data['code'] != department.code:
            existing_dept = Department.query.filter_by(code=data['code']).first()
            if existing_dept:
                return jsonify({'error': 'Department code already exists'}), 400

        # Update fields
        if 'name' in data:
            department.name = data['name']
        if 'code' in data:
            department.code = data['code']
        if 'head' in data:
            department.head = data['head']
        if 'contact_email' in data:
            department.contact_email = data['contact_email']

        db.session.commit()

        return jsonify({
            'message': 'Department updated successfully',
            'department': {
                'id': department.id,
                'name': department.name,
                'code': department.code,
                'head': department.head,
                'contact_email': department.contact_email,
                'created_at': department.created_at.isoformat(),
                'updated_at': department.updated_at.isoformat()
            }
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Department code already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/<int:department_id>', methods=['DELETE'])
@token_required
def delete_department(current_admin, department_id):
    """Delete a department."""
    try:
        department = Department.query.get_or_404(department_id)

        # Check if department has teachers or courses
        if department.teachers or department.courses:
            return jsonify({
                'error': 'Cannot delete department with associated teachers or courses'
            }), 400

        db.session.delete(department)
        db.session.commit()

        return jsonify({'message': 'Department deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/<int:department_id>/teachers', methods=['GET'])
@token_required
def get_department_teachers(current_admin, department_id):
    """Get all teachers in a department."""
    try:
        department = Department.query.get_or_404(department_id)

        return jsonify({
            'teachers': [{
                'id': teacher.id,
                'name': teacher.name,
                'email': teacher.email,
                'phone': teacher.phone,
                'specialization': teacher.specialization,
                'is_active': teacher.is_active
            } for teacher in department.teachers]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@departments_bp.route('/<int:department_id>/courses', methods=['GET'])
@token_required
def get_department_courses(current_admin, department_id):
    """Get all courses in a department."""
    try:
        department = Department.query.get_or_404(department_id)

        return jsonify({
            'courses': [{
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'teacher_id': course.teacher_id,
                'teacher_name': course.teacher.name if course.teacher else None,
                'weekly_sessions': course.weekly_sessions,
                'semester': course.semester,
                'year': course.year,
                'is_active': course.is_active
            } for course in department.courses]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500