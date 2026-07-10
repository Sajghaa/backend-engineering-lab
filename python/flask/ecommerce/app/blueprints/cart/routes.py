from flask import render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from app.models import Product
from app.blueprints.cart import cart_bp

@cart_bp.route('/')
def view_cart():
    cart = session.get('cart', {})
    items = []
    total = 0
    for product_id, qty in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * qty
            total += item_total
            items.append({
                'product': product,
                'quantity': qty,
                'item_total': item_total
            })
    return render_template('cart/view.html', items=items, total=total)

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Get quantity from form, default 1
    qty = request.form.get('quantity', 1, type=int)
    if qty < 1:
        qty = 1
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    session['cart'] = cart
    flash('Item added to cart.', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    qty = request.form.get('quantity', 1, type=int)
    cart = session.get('cart', {})
    if qty <= 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = qty
    session['cart'] = cart
    flash('Cart updated.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    flash('Item removed.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/clear', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    flash('Cart cleared.', 'info')
    return redirect(url_for('cart.view_cart'))