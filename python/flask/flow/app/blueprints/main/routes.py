from flask import render_template
from flask_login import current_user
from app.models import Project
from app.blueprints.main import main_bp

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        projects = Project.query.filter(
            (Project.created_by == current_user.id) |
            (Project.members.any(id=current_user.id))
        ).order_by(Project.created_at.desc()).limit(6).all()
    else:
        projects = []
    return render_template('main/index.html', projects=projects)

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/favicon.ico')
def favicon():
    return '', 204