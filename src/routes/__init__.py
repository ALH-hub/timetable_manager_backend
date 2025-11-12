"""
Import and register all route blueprints
"""
from .auth import auth_bp
from .departments import departments_bp
from .teachers import teachers_bp
from .rooms import rooms_bp
from .courses import courses_bp
from .timetables import timetables_bp
from .slots import slots_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(timetables_bp)
    app.register_blueprint(slots_bp)

__all__ = [
    'register_blueprints',
    'auth_bp',
    'departments_bp',
    'teachers_bp',
    'rooms_bp',
    'courses_bp',
    'timetables_bp',
    'slots_bp'
]