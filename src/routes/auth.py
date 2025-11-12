from flask import Blueprint, request, jsonify
from models.admin import Admin
from config.db import db
from services.jwt_service import generate_token, token_required, get_current_admin_from_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new admin user."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Check if admin already exists
        if Admin.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        if Admin.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        # Create new admin
        admin = Admin(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'admin')
        )
        admin.set_password(data['password'])

        db.session.add(admin)
        db.session.commit()

        # Generate token
        token = generate_token(admin.id)

        return jsonify({
            'message': 'Admin registered successfully',
            'token': token,
            'admin': {
                'id': admin.id,
                'username': admin.username,
                'email': admin.email,
                'role': admin.role
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login admin user."""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400

        # Find admin by username
        admin = Admin.query.filter_by(username=data['username']).first()

        if not admin or not admin.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Generate token
        token = generate_token(admin.id)

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'admin': {
                'id': admin.id,
                'username': admin.username,
                'email': admin.email,
                'role': admin.role
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_admin(current_admin):
    """Get current admin information."""
    return jsonify({
        'admin': {
            'id': current_admin.id,
            'username': current_admin.username,
            'email': current_admin.email,
            'created_at': current_admin.created_at.isoformat(),
            'updated_at': current_admin.updated_at.isoformat()
        }
    }), 200


@auth_bp.route('/change-password', methods=['PUT'])
@token_required
def change_password(current_admin):
    """Change admin password."""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400

        # Verify current password
        if not current_admin.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400

        # Update password
        current_admin.set_password(data['new_password'])
        db.session.commit()

        return jsonify({'message': 'Password changed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/update-profile', methods=['PUT'])
@token_required
def update_profile(current_admin):
    """Update admin profile."""
    try:
        data = request.get_json()

        # Update allowed fields
        if 'email' in data:
            # Check if email is already taken by another admin
            existing_admin = Admin.query.filter_by(email=data['email']).first()
            if existing_admin and existing_admin.id != current_admin.id:
                return jsonify({'error': 'Email already exists'}), 400
            current_admin.email = data['email']

        if 'username' in data:
            # Check if username is already taken by another admin
            existing_admin = Admin.query.filter_by(username=data['username']).first()
            if existing_admin and existing_admin.id != current_admin.id:
                return jsonify({'error': 'Username already exists'}), 400
            current_admin.username = data['username']

        db.session.commit()

        return jsonify({
            'message': 'Profile updated successfully',
            'admin': {
                'id': current_admin.id,
                'username': current_admin.username,
                'email': current_admin.email,
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
