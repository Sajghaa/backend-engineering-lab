from flask import render_template, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Project
from app.blueprints.admin import admin_bp

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    projects = Project.query.all()
    return render_template('admin/dashboard.html', users=users, projects=projects)

@admin_bp.route('/users/<int:user_id>/role/<role>')
@login_required
@admin_required
def change_role(user_id, role):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('Cannot change own role.', 'danger')
        return redirect(url_for('admin.dashboard'))
    if role in ['admin', 'project_manager', 'member']:
        user.role = role
        db.session.commit()
        flash(f'Role changed to {role}.', 'success')
    return redirect(url_for('admin.dashboard'))