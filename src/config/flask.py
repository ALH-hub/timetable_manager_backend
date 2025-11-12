from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from config.db import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.db.Config')


    db.init_app(app)
    CORS(app)

    Migrate(app, db)

    from models import Admin, Department, Teacher, Room, Course, TimeTable, TimeTableSlot

    @app.route('/')
    def welcome():
        return jsonify({'message': "Welcome to the Timetable Manager Backend!"})


    with app.app_context():
        #db.create_all()
        from routes import register_blueprints
        register_blueprints(app)

    return app