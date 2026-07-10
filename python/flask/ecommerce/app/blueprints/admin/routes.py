from flask import render_template, abort, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Order, Product, Category, User
from app.forms import ProductForm
from app.blueprints.admin import admin_bp

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_orders = Order.query.count()
    total_products = Product.query.count()
    total_users = User.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html',
                           total_orders=total_orders,
                           total_products=total_products,
                           total_users=total_users,
                           pending_orders=pending_orders,
                           recent_orders=recent_orders)

@admin_bp.route('/orders')
@login_required
@admin_required
def manage_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/orders/<int:order_id>/update', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')
    if status in ['pending', 'paid', 'shipped', 'delivered', 'cancelled']:
        order.status = status
        db.session.commit()
        flash('Order status updated.', 'success')
    else:
        flash('Invalid status.', 'danger')
    return redirect(url_for('admin.manage_orders'))

@admin_bp.route('/products')
@login_required
@admin_required
def manage_products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)