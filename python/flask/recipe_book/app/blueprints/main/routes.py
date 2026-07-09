from flask import render_template
from flask_login import current_user
from app.extensions import db
from app.models import Recipe
from app.blueprints.main import main_bp

@main_bp.route('/')
@main_bp.route('/index')
def index():
    # Show some recent recipes (public)
    recent_recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(6).all()
    # If user is logged in, show their stats
    if current_user.is_authenticated:
        my_recipes_count = Recipe.query.filter_by(user_id=current_user.id).count()
        favourites_count = current_user.favourite_recipes.count()
    else:
        my_recipes_count = 0
        favourites_count = 0
    return render_template('main/index.html', 
                           recent=recent_recipes,
                           my_recipes_count=my_recipes_count,
                           favourites_count=favourites_count)

@main_bp.route('/favicon.ico')
def favicon():
    return '', 204