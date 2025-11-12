from flask import Blueprint, request, jsonify
from models.teacher import Teacher
from models.department import Department
from config.db import db
from services.jwt_service import token_required
from sqlalchemy.exc import IntegrityError

teachers_bp = Blueprint('teachers', __name__, url_prefix='/api/teachers')


@teachers_bp.route('/', methods=['GET'])
@token_required
def get_teachers(current_admin):
    """Get all teachers with optional filtering."""
    try:
        # Get query parameters
        department_id = request.args.get('department_id', type=int)
        is_active = request.args.get('is_active', type=bool)

        # Build query
        query = Teacher.query

        if department_id:
            query = query.filter_by(department_id=department_id)

        if is_active is not None:
            query = query.filter_by(is_active=is_active)

        teachers = query.all()

        return jsonify({
            'teachers': [{
                'id': teacher.id,
                'name': teacher.name,
                'email': teacher.email,
                'phone': teacher.phone,
                'department_id': teacher.department_id,
                'department_name': teacher.department.name,
                'specialization': teacher.specialization,
                'is_active': teacher.is_active,
                'created_at': teacher.created_at.isoformat(),
                'updated_at': teacher.updated_at.isoformat(),
                'courses_count': len(teacher.courses)
            } for teacher in teachers]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@teachers_bp.route('/', methods=['POST'])
@token_required
def create_teacher(current_admin):
    """Create a new teacher."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'email', 'department_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Check if department exists
        department = Department.query.get(data['department_id'])
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        # Check if email already exists
        if Teacher.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        # Create new teacher
        teacher = Teacher(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            department_id=data['department_id'],
            specialization=data.get('specialization'),
            is_active=data.get('is_active', True)
        )

        db.session.add(teacher)
        db.session.commit()

        return jsonify({
            'message': 'Teacher created successfully',
            'teacher': {
                'id': teacher.id,
                'name': teacher.name,
                'email': teacher.email,
                'phone': teacher.phone,
                'department_id': teacher.department_id,
                'department_name': teacher.department.name,
                'specialization': teacher.specialization,
                'is_active': teacher.is_active,
                'created_at': teacher.created_at.isoformat(),
                'updated_at': teacher.updated_at.isoformat()
            }
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@teachers_bp.route('/<int:teacher_id>', methods=['GET'])
@token_required
def get_teacher(current_admin, teacher_id):
    """Get a specific teacher."""
    try:
        teacher = Teacher.query.get_or_404(teacher_id)

        return jsonify({
            'teacher': {
                'id': teacher.id,
                'name': teacher.name,
                'email': teacher.email,
                'phone': teacher.phone,
                'department_id': teacher.department_id,
                'department_name': teacher.department.name,
                'specialization': teacher.specialization,
                'is_active': teacher.is_active,
                'created_at': teacher.created_at.isoformat(),
                'updated_at': teacher.updated_at.isoformat(),
                'courses': [{
                    'id': course.id,
                    'name': course.name,
                    'code': course.code,
                    'semester': course.semester,
                    'year': course.year,
                    'weekly_sessions': course.weekly_sessions,
                    'is_active': course.is_active
                } for course in teacher.courses]
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@teachers_bp.route('/<int:teacher_id>', methods=['PUT'])
@token_required
def update_teacher(current_admin, teacher_id):
    """Update a teacher."""
    try:
        teacher = Teacher.query.get_or_404(teacher_id)
        data = request.get_json()

        # Check if department exists (if changing department)
        if 'department_id' in data:
            department = Department.query.get(data['department_id'])
            if not department:
                return jsonify({'error': 'Department not found'}), 404

        # Check if email already exists (if changing email)
        if data.get('email') and data['email'] != teacher.email:
            existing_teacher = Teacher.query.filter_by(email=data['email']).first()
            if existing_teacher:
                return jsonify({'error': 'Email already exists'}), 400

        # Update fields
        if 'name' in data:
            teacher.name = data['name']
        if 'email' in data:
            teacher.email = data['email']
        if 'phone' in data:
            teacher.phone = data['phone']
        if 'department_id' in data:
            teacher.department_id = data['department_id']
        if 'specialization' in data:
            teacher.specialization = data['specialization']
        if 'is_active' in data:
            teacher.is_active = data['is_active']

        db.session.commit()

        return jsonify({
            'message': 'Teacher updated successfully',
            'teacher': {
                'id': teacher.id,
                'name': teacher.name,
                'email': teacher.email,
                'phone': teacher.phone,
                'department_id': teacher.department_id,
                'department_name': teacher.department.name,
                'specialization': teacher.specialization,
                'is_active': teacher.is_active,
                'created_at': teacher.created_at.isoformat(),
                'updated_at': teacher.updated_at.isoformat()
            }
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@teachers_bp.route('/<int:teacher_id>', methods=['DELETE'])
@token_required
def delete_teacher(current_admin, teacher_id):
    """Delete a teacher."""
    try:
        teacher = Teacher.query.get_or_404(teacher_id)

        # Check if teacher has courses
        if teacher.courses:
            return jsonify({
                'error': 'Cannot delete teacher with assigned courses. Please reassign courses first.'
            }), 400

        db.session.delete(teacher)
        db.session.commit()

        return jsonify({'message': 'Teacher deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@teachers_bp.route('/<int:teacher_id>/courses', methods=['GET'])
@token_required
def get_teacher_courses(current_admin, teacher_id):
    """Get all courses taught by a teacher."""
    try:
        teacher = Teacher.query.get_or_404(teacher_id)

        return jsonify({
            'courses': [{
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'department_id': course.department_id,
                'department_name': course.department.name,
                'weekly_sessions': course.weekly_sessions,
                'semester': course.semester,
                'year': course.year,
                'is_active': course.is_active,
                'created_at': course.created_at.isoformat()
            } for course in teacher.courses]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@teachers_bp.route('/<int:teacher_id>/schedule', methods=['GET'])
@token_required
def get_teacher_schedule(current_admin, teacher_id):
    """Get teacher's timetable schedule."""
    try:
        teacher = Teacher.query.get_or_404(teacher_id)

        # Get all timetable slots for this teacher's courses
        from models.timetable import TimeTableSlot
        slots = TimeTableSlot.query.join(
            Teacher.courses
        ).filter(
            Teacher.id == teacher_id
        ).all()

        return jsonify({
            'schedule': [{
                'id': slot.id,
                'course_name': slot.course.name,
                'course_code': slot.course.code,
                'room_name': slot.room.name,
                'day_of_week': slot.day_of_week,
                'day_name': slot.day_name,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'notes': slot.notes,
                'timetable_name': slot.timetable.name
            } for slot in slots]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500