from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config.db import db
from models.user import User
from services.jwt_service import generate_token, token_required, refresh_token as token_refresh

auth_bp = Blueprint('auth', __name__, url_prefix=('/api/auth'))

@auth_bp.route('/register', methods=['POST'])
def register():
  """
  Register a new user.

  Expected JSON:
  {
    "name": "John Doe",
    "email": "john@example.com",
    "password": "yourpassword",
    "role": "student"
  }
  """
  try:
    data = request.get_json()

    # Validate required fields
    required_fields = ['name', 'email', 'password', 'role']
    for field in required_fields:
      if field not in data:
        return jsonify({'message': f'Missing required field: {field}'}), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
      return jsonify({'message': 'Email already registred'})

    # Hash the password
    hashed_password = generate_password_hash(data['password'])

    # Create user based on role
    role = data['role'].lower()

    if role == 'student':
      from models.student import Student
      new_user = Student(
        name = data['name'],
        email = data['email'],
        password = hashed_password
      )
    elif role == 'administrator':
      from models.administrator import Administrator
      new_user = Administrator(
        name = data['name'],
        email = data['email'],
        password = hashed_password
      )
    elif role == 'teacher':
      from models.teacher import Teacher
      new_user = Teacher(
        name = data['name'],
        email = data['email'],
        password = hashed_password
      )
    else:
      return jsonify({'message': 'Invalid role specified'}), 400

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    # Generate token
    token = generate_token(new_user.id)

    return jsonify({'message': 'User registered successfully',
                    'token': token,
                    'user': {
                      'id': new_user.id,
                      'name': new_user.name,
                      'email': new_user.email
                      }
                    }), 201

  except Exception as e:
    db.session.rollback()
    return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
  """
  User login.

  Expected JSON:
    {
      "email": "john@example.com",
      "password": "yourpassword"
    }
  """
  try:
      data = request.get_json()

      # Validate required fields
      required_fields = ['email', 'password']
      for field in required_fields:
        if field not in data:
          return jsonify({'message': f'Missing required field: {field}'}), 400

      # Find user by email
      user = User.query.filter_by(email=data['email']).first()
      if not user:
          return jsonify({'message': 'Invalid email or password'}), 401

      # Check password
      if not check_password_hash(user.password, data['password']):
          return jsonify({'message': 'Invalid email or password'}), 401

      # Generate token
      token = generate_token(user.id)

      return jsonify({'message': 'Login successful',
                      'token': token,
                      'user': {
                          'id': user.id,
                          'name': user.name,
                          'email': user.email
                      }
      }), 200

  except Exception as e:
      return jsonify({'message': f'Login failed: {str(e)}'}), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def me(current_user):
  """
  Get current user information.

  Expected Header:
    Authorization: Bearer <token>
  """
  return jsonify({
      'id': current_user.id,
      'name': current_user.name,
      'email': current_user.email,
      'role': current_user.type
  }), 200

@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
  """
  Refresh JWT token.

  Expected Header:
    Authorization: Bearer <token>
  """
  try:
      # Generate new token
      token = token_refresh(current_user.id)

      return jsonify({'message': 'Token refreshed successfully',
                      'token': token
      }), 200

  except Exception as e:
      return jsonify({'message': f'Token refresh failed: {str(e)}'}), 500