from routes.student import students_bp

def register_blueprints(app):
    """Register Flask blueprints with the app."""
    app.register_blueprint(students_bp)
    # Uncomment and add blueprints when routes are ready:
    # app.register_blueprint(foods_bp)
    # app.register_blueprint(persons_bp)
    # app.register_blueprint(food_recommendation_bp)
    # app.register_blueprint(allergy_probability_bp)
    # app.register_blueprint(food_consumptions_bp)
    # app.register_blueprint(weekly_plan_bp)
    # app.register_blueprint(buffet_bp)