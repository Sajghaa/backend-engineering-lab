from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, EmailField, PasswordField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    prep_time = IntegerField('Prep Time (minutes)', validators=[Optional(), NumberRange(min=0)])
    cook_time = IntegerField('Cook Time (minutes)', validators=[Optional(), NumberRange(min=0)])
    servings = IntegerField('Servings', validators=[Optional(), NumberRange(min=1)])
    category = SelectField('Category', choices=[
        ('', 'Select category'),
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('dessert', 'Dessert'),
        ('snack', 'Snack'),
        ('soup', 'Soup'),
        ('salad', 'Salad'),
        ('other', 'Other')
    ], validators=[Optional()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    ingredients = TextAreaField('Ingredients (one per line, e.g. "200 g flour")', validators=[DataRequired()])
    image = FileField('Recipe Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    submit = SubmitField('Save Recipe')

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[Optional()])
    category = SelectField('Category', choices=[('', 'All Categories'), 
                                                ('breakfast', 'Breakfast'),
                                                ('lunch', 'Lunch'),
                                                ('dinner', 'Dinner'),
                                                ('dessert', 'Dessert'),
                                                ('snack', 'Snack'),
                                                ('soup', 'Soup'),
                                                ('salad', 'Salad'),
                                                ('other', 'Other')],
                           validators=[Optional()])
    submit = SubmitField('Search')