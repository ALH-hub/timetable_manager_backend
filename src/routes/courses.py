from flask import Blueprint, request, jsonify
from models.course import Course
from models.department import Department
from models.teacher import Teacher
from config.db import db
from services.jwt_service import token_required
from sqlalchemy.exc import IntegrityError

courses_bp = Blueprint('courses', __name__, url_prefix='/api/courses')


@courses_bp.route('/', methods=['GET'])
@token_required
def get_courses(current_admin):
    """Get all courses with optional filtering."""
    try:
        # Get query parameters
        department_id = request.args.get('department_id', type=int)
        teacher_id = request.args.get('teacher_id', type=int)
        semester = request.args.get('semester')
        year = request.args.get('year', type=int)
        is_active = request.args.get('is_active', type=bool)

        # Build query
        query = Course.query

        if department_id:
            query = query.filter_by(department_id=department_id)

        if teacher_id:
            query = query.filter_by(teacher_id=teacher_id)

        if semester:
            query = query.filter_by(semester=semester)

        if year:
            query = query.filter_by(year=year)

        if is_active is not None:
            query = query.filter_by(is_active=is_active)

        courses = query.order_by(Course.code).all()

        return jsonify({
            'courses': [{
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'department_id': course.department_id,
                'department_name': course.department.name,
                'teacher_id': course.teacher_id,
                'teacher_name': course.teacher.name if course.teacher else None,
                'weekly_sessions': course.weekly_sessions,
                'semester': course.semester,
                'year': course.year,
                'is_active': course.is_active,
                'created_at': course.created_at.isoformat(),
                'updated_at': course.updated_at.isoformat()
            } for course in courses]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/', methods=['POST'])
@token_required
def create_course(current_admin):
    """Create a new course."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'code', 'department_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Check if department exists
        department = Department.query.get(data['department_id'])
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        # Check if teacher exists (if provided)
        if data.get('teacher_id'):
            teacher = Teacher.query.get(data['teacher_id'])
            if not teacher:
                return jsonify({'error': 'Teacher not found'}), 404

            # Check if teacher belongs to the same department
            if teacher.department_id != data['department_id']:
                return jsonify({'error': 'Teacher must belong to the same department'}), 400

        # Check if course code already exists
        if Course.query.filter_by(code=data['code']).first():
            return jsonify({'error': 'Course code already exists'}), 400

        # Validate weekly_sessions
        weekly_sessions = data.get('weekly_sessions', 1)
        if not isinstance(weekly_sessions, int) or weekly_sessions <= 0:
            return jsonify({'error': 'Weekly sessions must be a positive integer'}), 400

        # Create new course
        course = Course(
            name=data['name'],
            code=data['code'],
            department_id=data['department_id'],
            teacher_id=data.get('teacher_id'),
            weekly_sessions=weekly_sessions,
            semester=data.get('semester'),
            year=data.get('year'),
            is_active=data.get('is_active', True)
        )

        db.session.add(course)
        db.session.commit()

        return jsonify({
            'message': 'Course created successfully',
            'course': {
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'department_id': course.department_id,
                'department_name': course.department.name,
                'teacher_id': course.teacher_id,
                'teacher_name': course.teacher.name if course.teacher else None,
                'weekly_sessions': course.weekly_sessions,
                'semester': course.semester,
                'year': course.year,
                'is_active': course.is_active,
                'created_at': course.created_at.isoformat(),
                'updated_at': course.updated_at.isoformat()
            }
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Course code already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/<int:course_id>', methods=['GET'])
@token_required
def get_course(current_admin, course_id):
    """Get a specific course."""
    try:
        course = Course.query.get_or_404(course_id)

        # Get timetable slots for this course
        slots = course.timetable_slots

        return jsonify({
            'course': {
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'department_id': course.department_id,
                'department_name': course.department.name,
                'teacher_id': course.teacher_id,
                'teacher_name': course.teacher.name if course.teacher else None,
                'teacher_email': course.teacher.email if course.teacher else None,
                'weekly_sessions': course.weekly_sessions,
                'semester': course.semester,
                'year': course.year,
                'is_active': course.is_active,
                'created_at': course.created_at.isoformat(),
                'updated_at': course.updated_at.isoformat(),
                'schedule': [{
                    'id': slot.id,
                    'room_name': slot.room.name,
                    'room_id': slot.room_id,
                    'day_of_week': slot.day_of_week,
                    'day_name': slot.day_name,
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M'),
                    'notes': slot.notes,
                    'timetable_id': slot.timetable_id,
                    'timetable_name': slot.timetable.name
                } for slot in slots]
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/<int:course_id>', methods=['PUT'])
@token_required
def update_course(current_admin, course_id):
    """Update a course."""
    try:
        course = Course.query.get_or_404(course_id)
        data = request.get_json()

        # Check if department exists (if changing department)
        if 'department_id' in data:
            department = Department.query.get(data['department_id'])
            if not department:
                return jsonify({'error': 'Department not found'}), 404

        # Check if teacher exists and belongs to correct department (if changing teacher)
        if 'teacher_id' in data:
            if data['teacher_id']:  # If not None
                teacher = Teacher.query.get(data['teacher_id'])
                if not teacher:
                    return jsonify({'error': 'Teacher not found'}), 404

                # Use the department from data if provided, otherwise current course department
                dept_id = data.get('department_id', course.department_id)
                if teacher.department_id != dept_id:
                    return jsonify({'error': 'Teacher must belong to the same department'}), 400

        # Check if course code already exists (if changing code)
        if data.get('code') and data['code'] != course.code:
            existing_course = Course.query.filter_by(code=data['code']).first()
            if existing_course:
                return jsonify({'error': 'Course code already exists'}), 400

        # Validate weekly_sessions if provided
        if 'weekly_sessions' in data:
            if not isinstance(data['weekly_sessions'], int) or data['weekly_sessions'] <= 0:
                return jsonify({'error': 'Weekly sessions must be a positive integer'}), 400

        # Update fields
        if 'name' in data:
            course.name = data['name']
        if 'code' in data:
            course.code = data['code']
        if 'department_id' in data:
            course.department_id = data['department_id']
        if 'teacher_id' in data:
            course.teacher_id = data['teacher_id']
        if 'weekly_sessions' in data:
            course.weekly_sessions = data['weekly_sessions']
        if 'semester' in data:
            course.semester = data['semester']
        if 'year' in data:
            course.year = data['year']
        if 'is_active' in data:
            course.is_active = data['is_active']

        db.session.commit()

        return jsonify({
            'message': 'Course updated successfully',
            'course': {
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'department_id': course.department_id,
                'department_name': course.department.name,
                'teacher_id': course.teacher_id,
                'teacher_name': course.teacher.name if course.teacher else None,
                'weekly_sessions': course.weekly_sessions,
                'semester': course.semester,
                'year': course.year,
                'is_active': course.is_active,
                'created_at': course.created_at.isoformat(),
                'updated_at': course.updated_at.isoformat()
            }
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Course code already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@token_required
def delete_course(current_admin, course_id):
    """Delete a course."""
    try:
        course = Course.query.get_or_404(course_id)

        # Check if course has timetable slots
        if course.timetable_slots:
            return jsonify({
                'error': 'Cannot delete course with scheduled classes. Please remove all schedules first.'
            }), 400

        db.session.delete(course)
        db.session.commit()

        return jsonify({'message': 'Course deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/<int:course_id>/assign-teacher', methods=['PUT'])
@token_required
def assign_teacher(current_admin, course_id):
    """Assign a teacher to a course."""
    try:
        course = Course.query.get_or_404(course_id)
        data = request.get_json()

        if not data.get('teacher_id'):
            return jsonify({'error': 'teacher_id is required'}), 400

        teacher = Teacher.query.get(data['teacher_id'])
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404

        # Check if teacher belongs to the same department
        if teacher.department_id != course.department_id:
            return jsonify({'error': 'Teacher must belong to the same department as the course'}), 400

        # Check if teacher is active
        if not teacher.is_active:
            return jsonify({'error': 'Cannot assign inactive teacher'}), 400

        course.teacher_id = teacher.id
        db.session.commit()

        return jsonify({
            'message': 'Teacher assigned successfully',
            'course': {
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'teacher_id': course.teacher_id,
                'teacher_name': teacher.name
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/<int:course_id>/unassign-teacher', methods=['PUT'])
@token_required
def unassign_teacher(current_admin, course_id):
    """Unassign teacher from a course."""
    try:
        course = Course.query.get_or_404(course_id)

        course.teacher_id = None
        db.session.commit()

        return jsonify({
            'message': 'Teacher unassigned successfully',
            'course': {
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'teacher_id': None,
                'teacher_name': None
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500