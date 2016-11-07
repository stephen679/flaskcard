from wtforms import Form, BooleanField, StringField, PasswordField,IntegerField, FloatField, validators, ValidationError
from flask_wtf import FlaskForm
from models import *

# def point_check(negative=False,):
#     messsage =
#     def _point_check(form,field):
#         if not negative and field.data < 0.0:
#             raise ValidationError('Points must be a non-negative number')

class IdExists(object):
    def __init__(self,model,id):
        self.model = model
        self.id = id

    def exists(self):
        return len(self.model.query.filter_by(id=self.id)) != 0

class SemesterForm(FlaskForm):
    # possibly use InputRequired instead?
    season = StringField('season', [validators.Length(max=10),validators.DataRequired()])
    year = StringField('year', [validators.length(min=4,max=4),validators.DataRequired()])
    user_id = IntegerField('user_id', [validators.DataRequired(), IdExists(User)])

class AssignmentForm(FlaskForm):
    name = StringField('name', [validators.Length(max=128),validators.DataRequired()])
    earned_points = FloatField('earned_points', [validators.Length(max=4),validators.DataRequired()])
    total_points = FloatField('total_points', [validators.Length(max=4),validators.DataRequired()])
    description = StringField('description',[validators.Length(max=128)])
    course_id = IntegerField('course_id', [validators.DataRequired(),IdExists(Course)])
    category_id = IntegerField('category_id', [validators.DataRequired(), IdExists(Category)])


class CourseForm(FlaskForm):
    name = StringField('name', [validators.Length(max=128),validators.DataRequired()])
    instructor = StringField('instructor', [validators.Length(max=128), validators.DataRequired()])
    semester_id = IntegerField('semester_id',[validators.Length(max=4), validators.DataRequired()])

class CategoryForm(FlaskForm):
    name = StringField('name', [validators.Length(max=128),validators.DataRequired()])
    weight = FloatField('weight', [validators.Length(max=4),validators.DataRequired(), Weight])
