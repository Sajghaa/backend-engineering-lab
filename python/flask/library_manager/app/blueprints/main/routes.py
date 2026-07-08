from flask import render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Book
from app.blueprints.main import main_bp

@main_bp.route('/')
@main_bp.route('/index')
def index():
    if current_user.is_authenticated:
        books = Book.query.filter_by(user_id=current_user.id).order_by(Book.created_at.desc()).limit(5).all()
        total_books = Book.query.filter_by(user_id=current_user.id).count()
        read_books = Book.query.filter_by(user_id=current_user.id, status='read').count()
        avg_rating = db.session.query(db.func.avg(Book.rating)).filter_by(user_id=current_user.id).scalar() or 0
        return render_template('main/index.html', 
                               books=books, 
                               total=total_books, 
                               read=read_books, 
                               avg_rating=round(avg_rating, 1))
    return render_template('main/index.html', books=None, total=0, read=0, avg_rating=0)