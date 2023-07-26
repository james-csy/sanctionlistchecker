from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, validators

from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename

class SanctionSearch(FlaskForm):
    nameToSearch = StringField("Name")
    submit = SubmitField("Submit")


class SanctionSearchList(FlaskForm):
    textToSearch = TextAreaField(u'Text', [validators.length(max=1000)])
    submit = SubmitField("Submit")

class ExcelUploadWithLabels(FlaskForm):
    sheetName = StringField("Sheet Name")
    name = StringField("'Name' Header")
    desc = StringField("'Description' Header")
    loca = StringField("'Location' Header")
    upload = FileField('Excel File', validators=[FileRequired(),FileAllowed(['xlsx'], 'Excel Files (.xlsx) only!')])
    submit = SubmitField("Submit")