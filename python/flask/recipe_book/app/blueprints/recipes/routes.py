import os
import re
from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Recipe, Ingredient
from app.forms import RecipeForm, SearchForm
from app.blueprints.recipes import recipes_bp
from datetime import datetime
from app.models import recipe_ingredient

# Helper: save uploaded image
def save_image(form_image):
    if form_image:
        filename = secure_filename(form_image.filename)
        # Add timestamp to avoid collisions
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(datetime.utcnow().timestamp())}{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        form_image.save(filepath)
        return filename
    return None

# Helper: parse ingredients from textarea
def parse_ingredients(text):
    """
    Expects each line like: "quantity unit ingredient_name"
    e.g., "200 g flour", "2 eggs", "1 cup milk"
    We'll split by whitespace, but we need to handle multi-word ingredient names.
    We'll use a simple heuristic: the last part is the ingredient name, the rest is quantity+unit.
    Actually, we can ask users to put a comma: "200g, flour" or just use a simpler approach.
    To keep it simple: we'll split each line and treat everything before the last word as quantity+unit,
    and the last word as ingredient name. But better: we'll use regex to separate quantity and unit.
    We'll implement a more robust parser: 
    - Try to match pattern: (number) (unit) (ingredient) -> but units can vary.
    We'll simplify: each line will have at least two parts: quantity and ingredient name, unit optional.
    We'll just store the ingredient name as the whole line after the first token.
    """
    ingredients_list = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        # Try to split at first space: quantity+unit and name
        parts = line.split(maxsplit=1)
        if len(parts) == 1:
            # only ingredient name, assume quantity='' and unit=''
            ingredients_list.append((parts[0], '', ''))
        else:
            qty_unit = parts[0]  # e.g., "200g", "1 cup"
            name = parts[1]
            # Try to split quantity and unit (optional)
            # We'll keep it simple: store quantity as the whole string, unit as empty
            ingredients_list.append((name, qty_unit, ''))
    return ingredients_list

@recipes_bp.route('/')
def list_recipes():
    form = SearchForm(request.args)
    query = Recipe.query
    if form.search.data:
        search_term = f"%{form.search.data}%"
        query = query.filter(Recipe.title.ilike(search_term))
    if form.category.data:
        query = query.filter_by(category=form.category.data)
    # Order by newest
    recipes = query.order_by(Recipe.created_at.desc()).all()
    return render_template('recipes/list.html', recipes=recipes, form=form)

@recipes_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        # Handle image
        image_filename = save_image(form.image.data)
        # Create recipe
        recipe = Recipe(
            title=form.title.data,
            description=form.description.data,
            prep_time=form.prep_time.data,
            cook_time=form.cook_time.data,
            servings=form.servings.data,
            category=form.category.data,
            instructions=form.instructions.data,
            image_filename=image_filename,
            user_id=current_user.id
        )
        db.session.add(recipe)
        # Commit to get recipe.id for relationship
        db.session.commit()
        # Parse ingredients
        ingredients_data = parse_ingredients(form.ingredients.data)
        for name, quantity, unit in ingredients_data:
            # Find or create ingredient
            ingredient = Ingredient.query.filter_by(name=name).first()
            if not ingredient:
                ingredient = Ingredient(name=name)
                db.session.add(ingredient)
                db.session.commit()  # Need to commit to get id
            # Add association with quantity and unit
            # We need to insert into the junction table with extra fields
            # Since the table is defined, we can use the relationship's append with extra data?
            # It's easier to use the association object pattern, but we have a simple junction.
            # We'll execute raw insert or use the table's insert.
            # Better: we can use the recipe_ingredient table directly.
            stmt = recipe_ingredient.insert().values(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity=quantity,
                unit=unit
            )
            db.session.execute(stmt)
        db.session.commit()
        flash('Recipe added successfully!', 'success')
        return redirect(url_for('recipes.detail_recipe', recipe_id=recipe.id))
    return render_template('recipes/add.html', form=form)

@recipes_bp.route('/<int:recipe_id>')
def detail_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    # Get ingredients with quantities
    # We need to join with the junction table to get quantity/unit
    # Using SQLAlchemy's relationship with secondary doesn't automatically give extra fields.
    # We'll query the recipe_ingredient table.
    from app.models import recipe_ingredient
    ingredients_data = db.session.query(
        Ingredient.name,
        recipe_ingredient.c.quantity,
        recipe_ingredient.c.unit
    ).join(recipe_ingredient, Ingredient.id == recipe_ingredient.c.ingredient_id)\
     .filter(recipe_ingredient.c.recipe_id == recipe_id).all()
    
    # Check if current user has favourited
    is_favourite = False
    if current_user.is_authenticated:
        is_favourite = recipe in current_user.favourite_recipes
    return render_template('recipes/detail.html', recipe=recipe, 
                           ingredients=ingredients_data, is_favourite=is_favourite)

@recipes_bp.route('/<int:recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        abort(403)
    form = RecipeForm(obj=recipe)
    if form.validate_on_submit():
        # Update fields
        recipe.title = form.title.data
        recipe.description = form.description.data
        recipe.prep_time = form.prep_time.data
        recipe.cook_time = form.cook_time.data
        recipe.servings = form.servings.data
        recipe.category = form.category.data
        recipe.instructions = form.instructions.data
        
        # Handle image: if new image uploaded, replace old one
        if form.image.data:
            # Delete old image if exists
            if recipe.image_filename:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], recipe.image_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            recipe.image_filename = save_image(form.image.data)
        
        db.session.commit()
        flash('Recipe updated!', 'success')
        return redirect(url_for('recipes.detail_recipe', recipe_id=recipe.id))
    # Pre-fill ingredients textarea
    # We need to get current ingredients with quantities to display in textarea
    from app.models import recipe_ingredient
    current_ingredients = db.session.query(
        Ingredient.name,
        recipe_ingredient.c.quantity,
        recipe_ingredient.c.unit
    ).join(recipe_ingredient, Ingredient.id == recipe_ingredient.c.ingredient_id)\
     .filter(recipe_ingredient.c.recipe_id == recipe_id).all()
    if current_ingredients:
        # Build string: each line "quantity unit name" (if quantity or unit present)
        lines = []
        for name, qty, unit in current_ingredients:
            part = []
            if qty:
                part.append(qty)
            if unit:
                part.append(unit)
            part.append(name)
            lines.append(' '.join(part))
        form.ingredients.data = '\n'.join(lines)
    else:
        form.ingredients.data = ''
    return render_template('recipes/edit.html', form=form, recipe=recipe)

@recipes_bp.route('/<int:recipe_id>/delete', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        abort(403)
    # Delete image file
    if recipe.image_filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], recipe.image_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted.', 'info')
    return redirect(url_for('recipes.list_recipes'))

@recipes_bp.route('/<int:recipe_id>/favourite', methods=['POST'])
@login_required
def toggle_favourite(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe in current_user.favourite_recipes:
        current_user.favourite_recipes.remove(recipe)
        flash('Removed from favourites.', 'info')
    else:
        current_user.favourite_recipes.append(recipe)
        flash('Added to favourites!', 'success')
    db.session.commit()
    return redirect(url_for('recipes.detail_recipe', recipe_id=recipe.id))