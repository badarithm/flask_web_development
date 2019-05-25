from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired(), Length(max=255, min=2)])
    submit = SubmitField('Submit')