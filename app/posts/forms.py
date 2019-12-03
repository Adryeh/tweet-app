from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, TextAreaField, PasswordField, StringField, BooleanField, FileField
from  wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User


class CreatePost(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Content', validators=[DataRequired(), Length(max=500)])
    # picture = FileField('Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Say')
