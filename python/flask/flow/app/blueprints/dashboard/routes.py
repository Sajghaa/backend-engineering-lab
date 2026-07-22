from flask import render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models import Project, Task, Activity
from app.blueprints.dashboard import dashboard_bp
from app.models import Column

@dashboard_bp.route('/')
@login_required
def overview():
    # Get projects the user is part of
    projects = Project.query.filter(
        (Project.created_by == current_user.id) |
        (Project.members.any(id=current_user.id))
    ).all()
    project_ids = [p.id for p in projects]

    # Stats
    total_tasks = Task.query.filter(Task.column.has(board_id=Project.id)).filter(Project.id.in_(project_ids)).count()
    completed_tasks = Task.query.filter(Task.column.has(board_id=Project.id), Project.id.in_(project_ids), Task.column.has(name='Done')).count()
    # More stats...
    activities = Activity.query.filter(Activity.project_id.in_(project_ids)).order_by(Activity.timestamp.desc()).limit(20).all()

    # Data for charts: tasks per project
    tasks_per_project = db.session.query(
        Project.name, func.count(Task.id)
    ).join(Project, Project.id == Task.column.has(board_id=Project.id))\
     .filter(Project.id.in_(project_ids))\
     .group_by(Project.name).all()

    # Tasks by status (columns)
    # We'll compute per board, but for simplicity, we'll get counts per column name
    columns_data = db.session.query(
        Column.name, func.count(Task.id)
    ).join(Column, Column.id == Task.column_id)\
     .filter(Column.board.has(project_id=Project.id)).filter(Project.id.in_(project_ids))\
     .group_by(Column.name).all()

    return render_template('dashboard/overview.html',
                           projects=projects,
                           total_tasks=total_tasks,
                           completed_tasks=completed_tasks,
                           activities=activities,
                           tasks_per_project=tasks_per_project,
                           columns_data=columns_data)

@dashboard_bp.route('/data')
@login_required
def chart_data():
    # Return JSON for charts
    projects = Project.query.filter(
        (Project.created_by == current_user.id) |
        (Project.members.any(id=current_user.id))
    ).all()
    project_ids = [p.id for p in projects]
    # Tasks by status
    columns_data = db.session.query(
        Column.name, func.count(Task.id)
    ).join(Column, Column.id == Task.column_id)\
     .filter(Column.board.has(project_id=Project.id)).filter(Project.id.in_(project_ids))\
     .group_by(Column.name).all()
    return jsonify({
        'labels': [c[0] for c in columns_data],
        'data': [c[1] for c in columns_data]
    })