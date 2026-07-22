from flask import render_template
from flask_login import current_user
from app.models import Project
from app.blueprints.main import main_bp

@main_bp.route('/')
@main_bp.route('/index')
def index():
    if current_user.is_authenticated:
        projects = Project.query.filter(
            (Project.created_by == current_user.id) |
            (Project.members.any(id=current_user.id))
        ).order_by(Project.created_at.desc()).limit(6).all()
    else:
        projects = []
    return render_template('main/index.html', projects=projects)