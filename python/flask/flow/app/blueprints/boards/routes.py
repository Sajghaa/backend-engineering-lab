from flask import render_template, abort, request, jsonify, current_app
from flask_login import login_required, current_user
from app.extensions import db, socketio
from app.models import Board, Column, Task
from app.forms import TaskForm
from app.blueprints.boards import boards_bp
from flask_socketio import emit, join_room, leave_room

@boards_bp.route('/<int:board_id>')
@login_required
def view_board(board_id):
    board = Board.query.get_or_404(board_id)
    project = board.project
    if project.created_by != current_user.id and current_user not in project.members:
        abort(403)
    columns = Column.query.filter_by(board_id=board_id).order_by(Column.order).all()
    return render_template('boards/kanban.html', board=board, project=project, columns=columns)

# SocketIO events for real-time updates
@socketio.on('connect')
def handle_connect():
    # Join the board room based on board_id (passed from client)
    board_id = request.args.get('board_id')
    if board_id:
        join_room(f'board_{board_id}')
        emit('connected', {'msg': 'Connected to board'})

@socketio.on('disconnect')
def handle_disconnect():
    pass

@socketio.on('move_task')
def handle_move_task(data):
    # data: { task_id, from_column_id, to_column_id, new_order }
    task = Task.query.get(data['task_id'])
    if task:
        task.column_id = data['to_column_id']
        # We'll implement order reordering logic
        # For simplicity, just update column
        db.session.commit()
        # Broadcast to all clients in the board room
        emit('task_moved', data, room=f'board_{data["board_id"]}', include_self=False)


@boards_bp.route('/<int:board_id>/reorder', methods=['POST'])
@login_required
def reorder(board_id):
    board = Board.query.get_or_404(board_id)
    # Check permissions
    project = board.project
    if project.created_by != current_user.id and current_user not in project.members:
        abort(403)
    data = request.json
    # data: { column_id: [task_ids] } or [ {task_id, column_id, order} ]
    # We'll implement reordering inside column and across columns
    # For simplicity, we'll accept a list of tasks with column_id and order
    for item in data['items']:
        task = Task.query.get(item['id'])
        if task:
            task.column_id = item['column_id']
            task.order = item['order']
    db.session.commit()
    # Broadcast update
    socketio.emit('tasks_reordered', data, room=f'board_{board_id}')
    return jsonify({'status': 'ok'})