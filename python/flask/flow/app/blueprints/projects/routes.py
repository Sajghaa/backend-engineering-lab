from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Project, Board, Column
from app.forms import ProjectForm, BoardForm
from app.blueprints.projects import projects_bp

@projects_bp.route('/')
@login_required
def list_projects():
    projects = Project.query.filter(
        (Project.created_by == current_user.id) |
        (Project.members.any(id=current_user.id))
    ).order_by(Project.created_at.desc()).all()
    return render_template('projects/list.html', projects=projects)

@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data,
            created_by=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        # Add current user as member
        project.members.append(current_user)
        # Add default board with default columns
        board = Board(name='Kanban Board', project_id=project.id)
        db.session.add(board)
        db.session.commit()
        # Create default columns
        columns = ['To Do', 'In Progress', 'Done']
        for idx, col_name in enumerate(columns):
            col = Column(name=col_name, board_id=board.id, order=idx)
            db.session.add(col)
        db.session.commit()
        flash('Project created!', 'success')
        return redirect(url_for('projects.detail_project', project_id=project.id))
    return render_template('projects/create.html', form=form)

@projects_bp.route('/<int:project_id>')
@login_required
def detail_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.created_by != current_user.id and current_user not in project.members:
        abort(403)
    return render_template('projects/detail.html', project=project)

@projects_bp.route('/<int:project_id>/settings', methods=['GET', 'POST'])
@login_required
def project_settings(project_id):
    project = Project.query.get_or_404(project_id)
    if project.created_by != current_user.id and not current_user.is_admin:
        abort(403)
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        # Add member if selected
        if form.members.data and form.members.data != 0:
            user = User.query.get(form.members.data)
            if user and user not in project.members:
                project.members.append(user)
                db.session.commit()
                flash(f'Added {user.username} to project.', 'success')
        db.session.commit()
        flash('Project updated!', 'success')
        return redirect(url_for('projects.detail_project', project_id=project.id))
    return render_template('projects/settings.html', form=form, project=project)

@projects_bp.route('/<int:project_id>/add_board', methods=['POST'])
@login_required
def add_board(project_id):
    project = Project.query.get_or_404(project_id)
    if project.created_by != current_user.id and current_user not in project.members:
        abort(403)
    name = request.form.get('name')
    if name:
        board = Board(name=name, project_id=project.id)
        db.session.add(board)
        db.session.commit()
        # Create default columns
        for col_name in ['To Do', 'In Progress', 'Done']:
            col = Column(name=col_name, board_id=board.id, order=0)
            db.session.add(col)
        db.session.commit()
        flash('Board added.', 'success')
    else:
        flash('Board name required.', 'danger')
    return redirect(url_for('projects.detail_project', project_id=project.id))