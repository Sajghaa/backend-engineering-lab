import os
from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Product, Category
from app.forms import ProductForm, SearchForm
from app.blueprints.products import products_bp

def save_product_image(image_file):
    if image_file:
        filename = secure_filename(image_file.filename)
        # add timestamp to avoid collisions
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(datetime.utcnow().timestamp())}{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        return filename
    return None

@products_bp.route('/')
def list_products():
    form = SearchForm(request.args)
    query = Product.query
    if form.search.data:
        query = query.filter(Product.name.ilike(f"%{form.search.data}%"))
    if form.category.data and form.category.data != 0:
        query = query.filter_by(category_id=form.category.data)
    if form.min_price.data:
        query = query.filter(Product.price >= form.min_price.data)
    if form.max_price.data:
        query = query.filter(Product.price <= form.max_price.data)
    products = query.order_by(Product.created_at.desc()).all()
    return render_template('products/list.html', products=products, form=form)

@products_bp.route('/<int:product_id>')
def detail_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('products/detail.html', product=product)

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        image_filename = save_product_image(form.image.data)
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            category_id=form.category.data if form.category.data != 0 else None,
            image_filename=image_filename
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added!', 'success')
        return redirect(url_for('products.detail_product', product_id=product.id))
    return render_template('products/add.html', form=form)

@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_admin:
        abort(403)
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.category_id = form.category.data if form.category.data != 0 else None
        if form.image.data:
            # delete old image
            if product.image_filename:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            product.image_filename = save_product_image(form.image.data)
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('products.detail_product', product_id=product.id))
    return render_template('products/edit.html', form=form, product=product)

@products_bp.route('/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        abort(403)
    product = Product.query.get_or_404(product_id)
    # delete image
    if product.image_filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('products.list_products'))