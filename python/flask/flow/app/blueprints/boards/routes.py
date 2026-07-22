from flask import render_template, abort, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db, socketio
from app.models import Board, Column, Task
from . import boards_bp

@boards_bp.route('/<int:board_id>')
@login_required
def view_board(board_id):
    board = Board.query.get_or_404(board_id)
    project = board.project
    if project.created_by != current_user.id and current_user not in project.members:
        abort(403)
    columns = Column.query.filter_by(board_id=board_id).order_by(Column.order).all()
    return render_template('boards/kanban.html', board=board, project=project, columns=columns)

@boards_bp.route('/<int:board_id>/reorder', methods=['POST'])
@login_required
def reorder(board_id):
    board = Board.query.get_or_404(board_id)
    project = board.project
    if project.created_by != current_user.id and current_user not in project.members:
        abort(403)
    data = request.json
    # data: { items: [ { id, column_id, order } ] }
    for item in data['items']:
        task = Task.query.get(item['id'])
        if task:
            task.column_id = item['column_id']
            task.order = item['order']
    db.session.commit()
    socketio.emit('tasks_reordered', data, room=f'board_{board_id}')
    return jsonify({'status': 'ok'})

# SocketIO events handled in run.py or separate file
# We keep socketio.on('connect') etc. in run.py or a dedicated module.