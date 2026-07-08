from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, TextAreaField, IntegerField, SelectField, URLField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please log in.')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    genre = StringField('Genre', validators=[Optional()])
    year = IntegerField('Year', validators=[Optional(), NumberRange(min=1000, max=2026)])
    isbn = StringField('ISBN', validators=[Optional(), Length(max=20)])
    cover_url = URLField('Cover Image URL', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('to-read', 'To Read'),
        ('reading', 'Currently Reading'),
        ('read', 'Read')
    ], validators=[DataRequired()])
    rating = IntegerField('Rating (1-5)', validators=[Optional(), NumberRange(min=0, max=5)])