from wtforms import Form as NoCSRFForm, BooleanField, StringField, \
                            PasswordField,IntegerField, FloatField, validators, \
                            ValidationError,FormField,FieldList
from flask_wtf import Form
from models import *

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
    user_id = IntegerField('user_id', [validators.DataRequired(),IdValidate(User)])

    def validate(self):
        # Validate with the validators of the fields when initialized
        if not Form.validate(self):
            return False
        if Semester.query.filter_by(user_id=self.user_id.data,
                                    season=self.season.data,
                                    year=self.year.data).first() is not None:
            same = '%s %s already added' % (self.season.data,self.year.data)
            self.season.errors.append(same)
            self.year.errors.append(same)
            return False
        return True

class AssignmentForm(Form):
    name = StringField('name', [validators.Length(max=128),validators.DataRequired()])
    earned_points = FloatField('earned_points', [validators.DataRequired()])
    total_points = FloatField('total_points', [validators.DataRequired()])
    description = StringField('description',[validators.Length(max=128)],default="")
    category_id = IntegerField('category_id', [validators.DataRequired()])

class CategoryForm(Form):
    name = StringField('name', [validators.DataRequired()])
    weight = FloatField('weight', [validators.DataRequired()])

    def __init__(self,csrf_enabled=False,*args,**kwargs):
        super(CategoryForm,self).__init__(csrf_enabled=csrf_enabled,*args,**kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        # TODO: weird hack, try not to do this
        if float(self.data['weight'].data) > 1.0 or float(self.data['weight'].data) <= 0.0:
            self.weight.errors.append('Weight must be within 0.0 and 1.0')
            return False
        return True

class CourseForm(Form):
    name = StringField('name', [validators.Length(max=128),validators.DataRequired()])
    instructor = StringField('instructor', [validators.Length(max=128), validators.DataRequired()])
    semester_id = IntegerField('semester_id',[validators.DataRequired(), IdValidate(Semester)])

    # FieldList allows us to have an (optionally) extendable list for a form
    categories = FieldList(FormField(CategoryForm))

    def validate(self):
        if not Form.validate(self):
            return False
        if Course.query.filter_by(name=self.data['name'],
                            instructor=self.data['instructor'],
                            semester_id=self.data['semester_id']).first() is not None:
            self.semester_id.errors.append('This semester already has that course')
            return False
        return True
