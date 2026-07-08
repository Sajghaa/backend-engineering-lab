from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Book
from app.forms import BookForm
from app.blueprints.books import books_bp

@books_bp.route('/')
@login_required
def list_books():
    # Search and filter
    query = Book.query.filter_by(user_id=current_user.id)
    
    search = request.args.get('search')
    status_filter = request.args.get('status')
    genre_filter = request.args.get('genre')
    
    if search:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%')
            )
        )
    if status_filter and status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if genre_filter and genre_filter != 'all':
        query = query.filter_by(genre=genre_filter)
    
    books = query.order_by(Book.created_at.desc()).all()
    
    # Get unique genres for filter dropdown
    genres = db.session.query(Book.genre).filter_by(user_id=current_user.id).distinct().all()
    genres = [g[0] for g in genres if g[0]]
    
    return render_template('books/list.html', books=books, genres=genres)

@books_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            genre=form.genre.data,
            year=form.year.data,
            isbn=form.isbn.data,
            cover_url=form.cover_url.data,
            status=form.status.data,
            rating=form.rating.data or 0,
            user_id=current_user.id
        )
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('books.list_books'))
    return render_template('books/add.html', form=form)

@books_bp.route('/<int:book_id>')
@login_required
def detail_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.user_id != current_user.id:
        abort(403)
    return render_template('books/detail.html', book=book)

@books_bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.user_id != current_user.id:
        abort(403)
    
    form = BookForm(obj=book)
    if form.validate_on_submit():
        form.populate_obj(book)
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books.detail_book', book_id=book.id))
    return render_template('books/edit.html', form=form, book=book)

@books_bp.route('/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.user_id != current_user.id:
        abort(403)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted.', 'info')
    return redirect(url_for('books.list_books'))