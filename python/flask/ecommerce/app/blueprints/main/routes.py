from flask import render_template
from app.models import Product
from app.blueprints.main import main_bp

@main_bp.route('/')
def index():
    # Show featured products (latest 8)
    products = Product.query.order_by(Product.created_at.desc()).limit(8).all()
    return render_template('main/index.html', products=products)

@main_bp.route('/about')
def about():
    return render_template('main/about.html')


@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html')
    

@main_bp.route('/favicon.ico')
def favicon():
    return '', 204