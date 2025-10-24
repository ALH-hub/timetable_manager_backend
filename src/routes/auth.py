from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config.db import db
from models.user import User
from services.jwt_service import generate_token, token_required

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

    if role:
      pass

  except Exception as e:
    db.session.rollback()
    return jsonify({'message': f'Registration failed: {str(e)}'}), 500