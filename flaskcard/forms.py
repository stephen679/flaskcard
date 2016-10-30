from wtforms import Form, BooleanField, StringField, PasswordField, validators
from flask_wtf import FlaskForm
from models import *

class SemesterForm(FlaskForm):
    season = StringField('season', [validators.Length(max=10),validators.DataRequired()])
    year = StringField('year', [validators.length(min=4,max=4),validators.DataRequired()])

class AssignmentForm(FlaskForm):
    pass

class CourseForm(FlaskForm):
    pass
