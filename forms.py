from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, Length, ValidationError
import re

###########################
#User Forms
class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password')

    def validate_password(self, password_field):
        password = password_field.data
        if len(password) < 8:
            raise ValidationError('*Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('*Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            raise ValidationError('*Password must contain at least one lowercase letter')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('*Password must contain at least one special character')


#login form
class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=8)])


#Todo Form
class ToDoForm(FlaskForm):
    """Form for creating a new ToDo item."""

    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = StringField('Due Date', validators=[DataRequired()])