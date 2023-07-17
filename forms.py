from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, validators

class SanctionSearch(FlaskForm):
    nameToSearch = StringField("Name")
    submit = SubmitField("Submit")


class SanctionSearchList(FlaskForm):
    textToSearch = TextAreaField(u'Text', [validators.length(max=1000)])
    submit = SubmitField("Submit")