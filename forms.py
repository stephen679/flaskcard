from wtforms import Form, BooleanField, StringField, PasswordField,IntegerField, FloatField, validators, ValidationError
from flask_wtf import Form
from models import *

# def point_check(negative=False,):
#     messsage =
#     def _point_check(form,field):
#         if not negative and field.data < 0.0:
#             raise ValidationError('Points must be a non-negative number')

class IdValidate(object):
    def __init__(self,model):
        self.model = model

    def __call__(self,form,field,exists=True):
        id = field.data
        if id is None or id == "" or id < 0:
            raise ValidationError('Input does not exist or is invalid')

        if exists:
            # Make sure id exists
            if len(self.model.query.filter_by(id=id).all()) == 0:
                raise ValidationError('%s does not exist in the database' % id)
        else:
            # Make sure id does not exist already in the database
            if len(self.model.query.filter_by(id=id).all()) > 0:
                raise ValidationError('%s already exists in the database' % id)


class SemesterForm(Form):
    # possibly use InputRequired instead?
    season = StringField('season', [validators.Length(max=10),validators.DataRequired()])
    year = StringField('year', [validators.length(min=4,max=4),validators.DataRequired()])
    user_id = IntegerField('user_id', [validators.DataRequired(), IdValidate(User)])

class AssignmentForm(Form):
    name = StringField('name', [validators.Length(max=128),validators.DataRequired()])
    earned_points = FloatField('earned_points', [validators.DataRequired()])
    total_points = FloatField('total_points', [validators.DataRequired()])
    description = StringField('description',[validators.Length(max=128)],default="")
    category_id = IntegerField('category_id', [validators.DataRequired()])

class CourseForm(Form):
    name = StringField('name', [validators.Length(max=128),validators.DataRequired()])
    instructor = StringField('instructor', [validators.Length(max=128), validators.DataRequired()])
    semester_id = IntegerField('semester_id',[validators.DataRequired(), IdValidate(Semester)])

class CategoryForm(Form):
    name = StringField('name', [validators.Length(max=128),validators.DataRequired()])
    weight = FloatField('weight', [validators.Length(max=4),validators.DataRequired()])
