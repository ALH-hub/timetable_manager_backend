from routes.auth import auth_bp
from routes.departments import departments_bp
from routes.teachers import teachers_bp
from routes.rooms import rooms_bp
from routes.courses import courses_bp
from routes.timetables import timetables_bp
from routes.slots import slots_bp

def register_blueprints(app):
    """Register Flask blueprints with the app."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(timetables_bp)
    app.register_blueprint(slots_bp)