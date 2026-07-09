from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

# Junction table for Recipe <-> Ingredient with quantity and unit
recipe_ingredient = db.Table('recipe_ingredient',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'), primary_key=True),
    db.Column('quantity', db.String(50), nullable=False, default=''),
    db.Column('unit', db.String(20), nullable=False, default='')
)

# Junction table for User <-> Recipe (favourites)
favourites = db.Table('favourites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recipes = db.relationship('Recipe', backref='author', lazy=True, cascade='all, delete-orphan')
    favourite_recipes = db.relationship('Recipe', secondary=favourites, lazy='dynamic',
                                        backref=db.backref('favourited_by', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Ingredient {self.name}>'

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    prep_time = db.Column(db.Integer, nullable=True)   # minutes
    cook_time = db.Column(db.Integer, nullable=True)   # minutes
    servings = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    instructions = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)  # store just the filename
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to User (author)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Many-to-many with Ingredient via recipe_ingredient
    ingredients = db.relationship('Ingredient', secondary=recipe_ingredient,
                                  lazy='subquery',
                                  backref=db.backref('recipes', lazy=True))

    def __repr__(self):
        return f'<Recipe {self.title}>'