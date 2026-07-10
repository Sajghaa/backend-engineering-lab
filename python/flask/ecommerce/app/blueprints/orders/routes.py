from flask import render_template, abort
from flask_login import login_required, current_user
from app.models import Order
from app.blueprints.orders import orders_bp

@orders_bp.route('/')
@login_required
def list_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders/list.html', orders=orders)

@orders_bp.route('/<int:order_id>')
@login_required
def detail_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('orders/detail.html', order=order)