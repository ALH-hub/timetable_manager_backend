import jwt
import datetime
from functools import wraps
from flask import jsonify, current_app, request
from models.user import User

def generate_token(user_id, expires_in_hours=24):
  """
  Generate a JWT token for a given user ID.

  Args:
    user_id (int): The ID of the user.
    expires_in_hours (int): Token expiration time in hours. Default is 24 hours.

  Returns:
    str: The generated JWT token.
  """
  payload = {
    'user_id': user_id,
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expires_in_hours),
    'iat': datetime.datetime.utcnow()
  }

  token = jwt.encode(
    payload,
    current_app.config['SECRET_KEY'],  # type: ignore
    algorithm='HS256'
  )

  return token

def decode_token(token):
  """
  Decode and validate a JWT token.

  Args:
    token (str): The JWT token to decode.

  Returns:
    dict: The decoded token payload if valid.
  """
  try:
    payload = jwt.decode(
      token,
      current_app.config['SECRET_KEY'],  # type: ignore
      algorithms=['HS256']
    )

    return payload
  except jwt.ExpiredSignatureError:
    return None  # Token has expired
  except jwt.InvalidTokenError:
    return None  # Invalid token


def refresh_token(token, additional_hours=24):
  """
  Refresh a JWT token by extending its expiration time.

  Args:
    token (str): The JWT token to refresh.
    additional_hours (int): Additional hours to extend the token's validity. Default is 24 hours.

  Returns:
    str: The refreshed JWT token.
  """
  payload = decode_token(token)

  if not payload:
    return None  # Invalid or expired token

  new_exp = datetime.datetime.utcnow() + datetime.timedelta(hours=additional_hours)
  payload['exp'] = new_exp

  refreshed_token = jwt.encode(
    payload,
    current_app.config['SECRET_KEY'],  # type: ignore
    algorithm='HS256'
  )

  return refreshed_token

def token_required(f):
  """
  Decorator to protext routes with JWT authentication.

  Usage:
    @app.route('/protected')
    @token_required
    def protected_route(current_user):
      return jsonify({'message': f'Hello {current_user.name}'})
  """
  @wraps(f)
  def decorated(*args, **kwargs):
    token = None

    # Check for token in Authorization header
    if 'Authorization' in request.headers:
      auth_header = request.headers['Authorization']

      try:
        # Expect format: "Bearer <token>"
        token = auth_header.split(" ")[1]
      except IndexError:
        return jsonify({'message': 'Invalid token format. Use: Bearer <token>'}), 401

      if not token:
        return jsonify({'message': 'Token is missing!'}), 401

      # Decode and validate token
      payload = decode_token(token)

      if not payload:
        return jsonify({'message': 'Token is invalid!'})

      current_user = User.query.filter_by(id=payload['user_id']).first()

      if not current_user:
        return jsonify({'message': "User not found!"})

      return f(current_user, *args, **kwargs)

  return decorated


def optional_token(f):
  """
  Decorator that allows both authenticated and unauthenticated access.
  If token is present and valid, current_user is provided else None
  """
  @wraps(f)
  def decorated(*args, **kwargs):
    token = None
    current_user = None

    if 'Authorization' in request.headers:
      auth_header = request.headers['Authorization']

      try:
        token = auth_header.split(" ")[1]
        payload = decode_token(token)

        if payload:
          current_user = User.query.filter_by(id=payload["user_id"]).first
      except IndexError:
        pass

      return f(current_user, *args, **kwargs)

  return decorated
