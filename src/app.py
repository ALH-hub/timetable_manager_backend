from config.db import db
from config.flask import create_app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        import models # Import all models to ensure they're registered
        db.create_all()

    app.run(debug=True)