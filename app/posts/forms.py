from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField
from wtforms.validators import DataRequired, Length



class CreatePost(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Content', validators=[DataRequired(), Length(max=500)])
    # picture = FileField('Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Say')
