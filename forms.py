from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, EmailField, PasswordField
from wtforms.validators import InputRequired, Optional, Email, Length, EqualTo

class SignupForm(FlaskForm):
    """Form for adding users"""

    username = StringField('Username', validators=[InputRequired(), Length(min=6, max=20, message="Usernames must be at least 6 characters and cannot exceed 20 characters.")])

    email = EmailField('Email Address', validators=[InputRequired(), Email()])

    password = PasswordField('Password', validators=[Length(min=6, max=50), InputRequired()])
    confirm = PasswordField('Confirm Password', validators=[EqualTo('confirm', message='Passwords must match.')])


class LoginForm(FlaskForm):
    """Login form"""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class UpdateProfileForm(FlaskForm):
    """Form for updating profile"""

    username = StringField('Username', validators=[Length(min=6, max=20, message="Usernames must be at least 6 characters and cannot exceed 20 characters.")])

    email = EmailField('Email Address', validators=[Email()])

    password = PasswordField('New Password', validators=[Length(min=6, max=50)])
    confirm = PasswordField('Confirm Password', validators=[EqualTo('confirm', message='Passwords must match.')])