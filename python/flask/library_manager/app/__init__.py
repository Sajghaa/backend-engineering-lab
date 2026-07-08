from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf
from app.models import User  # Import models so SQLAlchemy knows about them

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.books import books_bp
    from app.blueprints.main import main_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(books_bp, url_prefix='/books')
    app.register_blueprint(main_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404  # We'll create this later

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('500.html'), 500

    return app

# To avoid circular import in routes, we import render_template here
from flask import render_template