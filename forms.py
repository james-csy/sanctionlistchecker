from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, validators

class SanctionSearch(FlaskForm):
    nameToSearch = StringField("Name")
    submit = SubmitField("Submit")


class SanctionSearchList(FlaskForm):
    textToSearch = TextAreaField(u'Text', [validators.length(max=1000)])
    submit = SubmitField("Submit")

class ExcelUploadWithLabels(FlaskForm):
    name = StringField("'Name' Header")
    desc = StringField("'Description' Header")
    loca = StringField("'Location' Header")
    submit = SubmitField("Submit")