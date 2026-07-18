from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, EmailField, PasswordField, TextAreaField, SelectField, DateTimeField, IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from app.models import User, Project

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username taken.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    members = SelectField('Add Members', coerce=int, validators=[Optional()])
    submit = SubmitField('Create Project')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.members.choices = [(0, 'Select Member')] + [(u.id, u.username) for u in User.query.filter(User.role != 'admin').all()]

class BoardForm(FlaskForm):
    name = StringField('Board Name', validators=[DataRequired()])
    submit = SubmitField('Add Board')

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    priority = SelectField('Priority', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    due_date = DateTimeField('Due Date', format='%Y-%m-%d %H:%M', validators=[Optional()])
    assignee = SelectField('Assign To', coerce=int, validators=[Optional()])
    attachment = FileField('Attach File', validators=[FileAllowed(['jpg','jpeg','png','gif','pdf','doc','docx','txt'], 'Allowed files only')])
    submit = SubmitField('Save Task')

    def __init__(self, project_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project_id:
            # Get members of the project
            project = Project.query.get(project_id)
            if project:
                choices = [(0, 'Unassigned')] + [(u.id, u.username) for u in project.members]
                self.assignee.choices = choices
        else:
            self.assignee.choices = [(0, 'Select user')]