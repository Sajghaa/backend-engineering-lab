import os
from flask import Flask, render_template
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf, socketio, mail
from app.models import User, Project, Board, Column, Task, Attachment, Activity

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")  # for development

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.projects import projects_bp
    from app.blueprints.boards import boards_bp
    from app.blueprints.tasks import tasks_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(boards_bp, url_prefix='/boards')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('500.html'), 500

    # Custom filters
    @app.template_filter('datetime')
    def datetime_filter(value):
        if value:
            return value.strftime('%Y-%m-%d %H:%M')
        return ''

    return app