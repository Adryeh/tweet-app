from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import SubmitField, TextField, PasswordField, StringField, BooleanField, FileField
from  wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    submit = SubmitField('Register')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username exists. Please choose another!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email exists. Please choose another!')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    name = StringField('Name')
    second_name = StringField('Second Name')
    username: StringField = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email: StringField = StringField('E-mail', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username exists. Please choose another!')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email exists. Please choose another!')