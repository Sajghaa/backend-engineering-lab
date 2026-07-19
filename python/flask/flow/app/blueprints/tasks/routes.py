import os
from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db, socketio
from app.models import Task, Project, Attachment, Activity
from app.forms import TaskForm
from app.blueprints.tasks import tasks_bp
from datetime import datetime

def save_attachment(file):
    if file:
        original = secure_filename(file.filename)
        # Add timestamp to avoid name collisions
        name, ext = os.path.splitext(original)
        filename = f"{name}_{int(datetime.utcnow().timestamp())}{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename, original
    return None, None

@tasks_bp.route('/<int:task_id>')
@login_required
def detail_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.column.board.project
    if project.created_by != current_user.id and current_user not in project.members:
        abort(403)
    return render_template('tasks/detail.html', task=task)

@tasks_bp.route('/add/<int:column_id>', methods=['GET', 'POST'])
@login_required
def add_task(column_id):
    column = Column.query.get_or_404(column_id)
    project = column.board.project
    if project.created_by != current_user.id and current_user not in project.members:
        abort(403)
    form = TaskForm(project_id=project.id)
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            column_id=column.id,
            assignee_id=form.assignee.data if form.assignee.data != 0 else None,
            order=Task.query.filter_by(column_id=column.id).count()  # append at end
        )
        db.session.add(task)
        db.session.flush()  # to get id

        # Handle attachment
        if form.attachment.data:
            filename, original = save_attachment(form.attachment.data)
            if filename:
                att = Attachment(filename=filename, original_filename=original, task_id=task.id)
                db.session.add(att)

        db.session.commit()
        # Log activity
        activity = Activity(
            user_id=current_user.id,
            project_id=project.id,
            action=f'Added task "{task.title}" to column "{column.name}"'
        )
        db.session.add(activity)
        db.session.commit()
        # Emit via socket
        socketio.emit('task_added', {'task_id': task.id, 'column_id': column.id, 'board_id': column.board_id},
                      room=f'board_{column.board_id}')
        flash('Task created!', 'success')
        return redirect(url_for('boards.view_board', board_id=column.board_id))
    return render_template('tasks/add.html', form=form, column=column)

@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.column.board.project
    if project.created_by != current_user.id and current_user not in project.members:
        abort(403)
    form = TaskForm(project_id=project.id, obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.priority = form.priority.data
        task.due_date = form.due_date.data
        task.assignee_id = form.assignee.data if form.assignee.data != 0 else None
        if form.attachment.data:
            filename, original = save_attachment(form.attachment.data)
            if filename:
                att = Attachment(filename=filename, original_filename=original, task_id=task.id)
                db.session.add(att)
        db.session.commit()
        # Log activity
        activity = Activity(
            user_id=current_user.id,
            project_id=project.id,
            action=f'Updated task "{task.title}"'
        )
        db.session.add(activity)
        db.session.commit()
        flash('Task updated!', 'success')
        return redirect(url_for('tasks.detail_task', task_id=task.id))
    return render_template('tasks/edit.html', form=form, task=task)

@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.column.board.project
    if project.created_by != current_user.id and current_user not in project.members:
        abort(403)
    # Delete attachments from disk
    for att in task.attachments:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], att.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    db.session.delete(task)
    db.session.commit()
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        project_id=project.id,
        action=f'Deleted task "{task.title}"'
    )
    db.session.add(activity)
    db.session.commit()
    flash('Task deleted.', 'info')
    return redirect(url_for('boards.view_board', board_id=task.column.board_id))