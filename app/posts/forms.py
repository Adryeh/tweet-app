from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, TextAreaField, PasswordField, StringField, BooleanField, FileField
from  wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User


class CreatePost(FlaskForm):
    title = StringField('Title')
    text = TextAreaField('Content')
    submit = SubmitField('Say')
