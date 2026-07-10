import stripe
from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Order, OrderItem, Product
from app.forms import CheckoutForm
from app.blueprints.checkout import checkout_bp

@checkout_bp.route('/')
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart.view_cart'))
    # Calculate total
    total = 0
    items = []
    for product_id, qty in cart.items():
        product = Product.query.get(int(product_id))
        if product and product.stock >= qty:
            item_total = product.price * qty
            total += item_total
            items.append({'product': product, 'quantity': qty, 'item_total': item_total})
        else:
            flash(f'Product {product.name if product else "unknown"} is out of stock.', 'danger')
            return redirect(url_for('cart.view_cart'))
    form = CheckoutForm()
    return render_template('checkout/checkout.html', form=form, items=items, total=total)

@checkout_bp.route('/create', methods=['POST'])
@login_required
def create_order():
    form = CheckoutForm()
    if form.validate_on_submit():
        cart = session.get('cart', {})
        if not cart:
            flash('Cart empty.', 'warning')
            return redirect(url_for('cart.view_cart'))
        # Create order
        total = 0
        order_items_data = []
        for product_id, qty in cart.items():
            product = Product.query.get(int(product_id))
            if not product or product.stock < qty:
                flash(f'Product {product.name if product else "unknown"} is out of stock.', 'danger')
                return redirect(url_for('cart.view_cart'))
            total += product.price * qty
            order_items_data.append((product, qty, product.price))
        # Generate order number
        import random, string
        order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        order = Order(
            order_number=order_number,
            user_id=current_user.id,
            total_amount=total,
            shipping_address=form.shipping_address.data,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()  # to get order.id
        for product, qty, price in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                price=price
            )
            db.session.add(order_item)
            # reduce stock
            product.stock -= qty
        db.session.commit()
        # clear cart
        session.pop('cart', None)
        flash('Order placed!', 'success')
        # Redirect to payment (Stripe)
        return redirect(url_for('checkout.payment', order_id=order.id))
    return render_template('checkout/checkout.html', form=form)

@checkout_bp.route('/payment/<int:order_id>')
@login_required
def payment(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    # Set up Stripe Checkout session
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Order #{order.order_number}',
                    },
                    'unit_amount': int(order.total_amount * 100),  # cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('checkout.success', order_id=order.id, _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('checkout.cancel', order_id=order.id, _external=True),
        )
        # Save payment intent id
        order.stripe_payment_intent_id = checkout_session.payment_intent
        db.session.commit()
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'Payment error: {str(e)}', 'danger')
        return redirect(url_for('orders.detail_order', order_id=order.id))

@checkout_bp.route('/success/<int:order_id>')
@login_required
def success(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    order.status = 'paid'
    db.session.commit()
    flash('Payment successful! Thank you for your order.', 'success')
    return render_template('checkout/success.html', order=order)

@checkout_bp.route('/cancel/<int:order_id>')
@login_required
def cancel(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    # Optionally delete order or keep as pending
    flash('Payment cancelled.', 'info')
    return render_template('checkout/cancel.html', order=order)