from flask_wtf import FlaskForm
from wtforms import Form, StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(Form):
    search = StringField('Query', validators=[DataRequired()])
    submit = SubmitField('Give me results!')
