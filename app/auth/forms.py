from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 255), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 255), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 255),
        Regexp('^[a-zA-Z][a-zA-Z0-9_.]*$', 0, 'Usernames should be composed fo letters, numbers, underscores and dots')
    ])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords have to be the same')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None :
            raise ValidationError("Email {} is already registered".format(field.data))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError('Username {} is already in use'.format(field.data))
