import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import jsonify, current_app, request

def generate_token(admin_id, expires_in_hours=24):
    """
    Generate a JWT token for a given admin user ID.

    Args:
        admin_id (int): The ID of the admin user.
        expires_in_hours (int): Token expiration time in hours. Default is 24 hours.

    Returns:
        str: The generated JWT token.
    """
    payload = {
        'admin_id': admin_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
        'iat': datetime.now(timezone.utc),
        'type': 'access'
    }

    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    return token

def decode_token(token):
    """
    Decode and validate a JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict or None: The decoded token payload if valid, None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
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
        str or None: The refreshed JWT token if successful, None if invalid/expired.
    """
    payload = decode_token(token)

    if not payload:
        return None  # Invalid or expired token

    # Create new payload with extended expiration
    new_payload = {
        'admin_id': payload.get('admin_id'),
        'exp': datetime.now(timezone.utc) + timedelta(hours=additional_hours),
        'iat': datetime.now(timezone.utc),
        'type': 'access'
    }

    refreshed_token = jwt.encode(
        new_payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    return refreshed_token

def token_required(f):
    """
    Decorator to protect routes with JWT authentication.

    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_admin):
            return jsonify({'message': f'Hello {current_admin.username}'})
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
            return jsonify({'message': 'Token is invalid!'}), 401

        # Import Admin here to avoid circular imports
        from models.admin import Admin
        current_admin = Admin.query.filter_by(id=payload['admin_id']).first()

        if not current_admin:
            return jsonify({'message': "Admin user not found!"}), 401

        return f(current_admin, *args, **kwargs)

    return decorated


def optional_token(f):
    """
    Decorator that allows both authenticated and unauthenticated access.
    If token is present and valid, current_admin is provided, else None.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        current_admin = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']

            try:
                token = auth_header.split(" ")[1]
                payload = decode_token(token)

                if payload:
                    # Import Admin here to avoid circular imports
                    from models.admin import Admin
                    current_admin = Admin.query.filter_by(id=payload["admin_id"]).first()
            except (IndexError, KeyError):
                # If there's any error with token parsing, just continue with None user
                pass

        return f(current_admin, *args, **kwargs)

    return decorated


def extract_token_from_request():
    """
    Extract JWT token from request headers.

    Returns:
        str or None: The token if present and properly formatted, None otherwise.
    """
    if 'Authorization' not in request.headers:
        return None

    auth_header = request.headers['Authorization']

    try:
        # Expect format: "Bearer <token>"
        return auth_header.split(" ")[1]
    except IndexError:
        return None


def get_current_admin_from_token():
    """
    Get the current admin from the JWT token in the request.

    Returns:
        Admin or None: The admin object if token is valid, None otherwise.
    """
    token = extract_token_from_request()

    if not token:
        return None

    payload = decode_token(token)

    if not payload:
        return None

    # Import Admin here to avoid circular imports
    from models.admin import Admin
    return Admin.query.filter_by(id=payload.get('admin_id')).first()


def is_token_expired(token):
    """
    Check if a token is expired.

    Args:
        token (str): The JWT token to check.

    Returns:
        bool: True if expired, False if valid, None if invalid token.
    """
    try:
        jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return False  # Token is valid and not expired
    except jwt.ExpiredSignatureError:
        return True  # Token is expired
    except jwt.InvalidTokenError:
        return None  # Token is invalid
