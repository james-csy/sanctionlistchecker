from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class SanctionSearch(FlaskForm):
    nameToSearch = StringField("Name")
    submit = SubmitField("Submit")