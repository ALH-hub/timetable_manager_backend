from src import create_app


app = create_app()

if __name__ == '__main__':
    from src.config import db
    with app.app_context():
        db.create_all()
    app.run(debug=True)