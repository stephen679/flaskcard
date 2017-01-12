import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort,render_template, flash
#from flaskext.mysql import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user , logout_user , current_user , login_required
from contextlib import closing # helps initialize a database so we don't have to hardcode
from models import *
from forms import *

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'development key'
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = 'default'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/flaskcard'

# db comes from models.py
# TODO: create database if it doesn't exist. Or should that be admin's manual job?
db.init_app(app)
lm = LoginManager()
lm.init_app(app)

def get_current_user():
    """
    Utilize the g module to keep track of who is currently logged in
    Args:
        None
    """
    if g.user is None:
        return None
    return User.query.filter_by(id=current_user.get_id()).first()

@app.before_request
def before_request():
    """
    Ensure that the requests you make are associated with a user (for the most part)
    """
    g.user = current_user

@app.before_first_request
def initialize_database():
    """
    Create database models and relationships before the first request
    """
    db.engine.execute('CREATE DATABASE IF NOT EXISTS flaskcard')
    db.create_all()
    # initialize a default category so that users can populate all their grades first

@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.errorhandler(404)
def error_404_response(error):
    return render_template('error.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    # Ensure unique usernames!
    if User.query.filter_by(username=request.form['username'].lower()).first() is not None:
        flash('That username is already taken')
        return redirect(url_for('register'))
    new_user = User(username=request.form['username'],password=request.form['password'])
    db.session.add(new_user)
    db.session.commit()
    flash('User registered!')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    err = None
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        registered_user = User.query.filter_by(username=username.lower(),password=password).first()
        if registered_user is None:
            flash('Username or Password is invalid' , 'error')
            return redirect(url_for('login'))
        login_user(registered_user)
        flash('You\'re logged in')
        # Go to the next page specified in HTML or default semseters
        return redirect(request.args.get('next') or url_for('semesters'))
    return render_template('login.html', error=err)

@app.route('/logout')
@login_required
def logout():
    """
    If logged in, log the user out
    """
    logout_user()
    flash('You logged out')
    return redirect(url_for('login'))

@app.route('/',methods=["GET","POST"])
@login_required
def semesters():
    """
    Show semesters for the logged-in user
    """
    if request.method == "POST":
        f = SemesterForm(request.form)
        new_semester = Semester()
        if f.validate_on_submit():
            f.populate_obj(new_semester)
            db.session.add(new_semester)
            db.session.commit()
        else:
            flash(f.errors)
    return render_template('overview.html', user=current_user,
                                            form=SemesterForm())

@app.route('/semester', methods = ["GET","POST"])
@login_required
def semester():
    if request.method == "POST":
        # Partially initialize the course form, and then manually add
        # categories to it. Then we have all the information to validate a course
        # and its category weights.
        f = CourseForm(request.form)
        def extract(key_to_extract,form):
            arr = filter(lambda kv: kv.startswith(key_to_extract),form)
            arr.sort()
            return map(lambda key: form[key], arr)

        category_names = extract('category',request.form)
        category_weights = extract('weight',request.form)

        for i in xrange(len(category_names)):
            # LEARNING EXPRERIENCE: when appending an entry, don't think of it
            # as appending a FORM. think of it as appending the OBJECT that's related
            # to the form. Hence, you only need a dict that corresponds with the model.
            f.categories.append_entry({'name'   : category_names[i],
                                       'weight' : category_weights[i]})
        if f.validate_on_submit():
            # TODO: create Course and Category objects at the same time?
            #       i.e, find a way to do f.populate_obj(Course), with course
            #       already having empty category objects in it
            new_course = Course(request.form)
            db.session.add(new_course)
            db.session.commit()
            for i in xrange(len(category_names)):
                db.session.add(Category(name=category_names[i],
                                        weight=category_weights[i],
                                        course_id=new_course.id))
            db.session.commit()
            flash('Course added!')
        else:
            flash(f.errors)
        season = request.form['season']
        year = request.form['year']
    else:
        try:
            season = request.args.get('season')
            year = request.args.get('year')
        except:
            flash('Semester does not exist in the database')
            return redirect(url_for('semesters'))
    semester = Semester.query.filter_by(season=season,year=year,user_id=current_user.id).first()
    if semester is None:
        flash('The semester you tried accessing does not exist in the database')
        return redirect(url_for('semesters'))
    return render_template('semester.html', semester=semester,form=CourseForm())

@app.route('/course/<course_id>', methods=['GET','POST'])
@login_required
def course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return redirect(url_for('semesters'))
    semester = Semester.query.filter_by(id=course.semester_id).first()

    if request.method == "POST":
        #TODO: validate course_id and category_id!!!!
        # must ensure all elements in form are present!
        f = AssignmentForm(request.form)
        if f.validate():
            new_assignment = Assignment()
            f.populate_obj(new_assignment)
            db.session.add(new_assignment)
            db.session.commit()
        else:
            flash(f.errors)
        return redirect(url_for('course', course_id=course_id))

    try:
        course_avg = course_average(course)
    except:
        course_avg = "No points earned so far"
    context = {
        'course' : course,
        'semester' : semester,
        'categories' : Category.query.filter_by(course_id=course.id).all(),
        'course_avg' : course_avg,
        'form' : CourseForm(),
    }
    return render_template('course.html',**context)

@app.route('/category/<course_id>',methods=['GET'])
@login_required
def category(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        flash('Course not found')
        return redirect(url_for('semesters'))
    assignments = course.assignments.all()
    categories = set([Category.query.filter_by(id=a.category_id).first() for a in assignments])
    return render_template('category.html',categories=categories)

@app.route('/category/add', methods=['POST'])
@login_required
def add_category():
    name = request.form['name'].strip().lower()
    weight = request.form['weight']
    new_category = Category(name,request.form['weight'])
    if Category.query.filter_by(name=name,weight=weight).first() is not None:
        flash('Category already added')
        return redirect(url_for('add_category'))
    db.session.add(new_category)
    db.session.commit()
    return redirect(url_for('semesters'))

@app.route('/course/<course_id>/assignments/<assignment_id>', methods=['GET','POST'])
@login_required
def assignment(course_id,assignment_id):
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if assignment is None:
        flash('Assignment does not exist in our database!')
        return redirect(url_for('course',course_id=course_id))
    context = {
        'assignment' : assignment,
        'course_id' : course_id
    }
    return render_template('assignment.html', **context)

@app.route('/course/<course_id>/assignments/<assignment_id>/delete', methods=["GET"])
def delete_assignment(course_id,assignment_id):
    # TODO: use AJAX/javascript to handle DELETE requests (the method would just be "delete")
    # TODO: create a get_or_not_exists function that generalizes across models
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if assignment is None:
        flash('Assignment does not exist in our database!')
    else:
        flash('Successfully deleted assignment')
        db.session.delete(assignment)
        db.session.commit()
    return redirect(url_for('course',course_id=course_id))

@app.route('/course/<course_id>/assignments/<assignment_id>/update', methods=['POST'])
@login_required
def update_assignment(course_id,assignment_id):
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if assignment is None:
        flash('Assignment does not exist in our database!')
        return redirect(url_for('course',course_id=course_id))
    assignment.earned_points = request.form['points_earned']
    assignment.total_points = request.form['total_points']
    db.session.commit()
    return redirect(url_for('compute',course_id=course_id))

@app.route('/course/<course_id>/compute', methods=['GET'])
@login_required
def compute(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return redirect(url_for('semester'))
    try:
        percent = course_average(course)
        total_weight = completed_categories_weight(course)
        flash("Grade for this course: %.2f%%. %.2f%% total weight counted" % (percent/total_weight*100.0,total_weight*100.0))
        if (percent*100.0) > 100.0:
            flash("Grade for this course is over 100%. Ensure that this is correct and that the category weights are valid.")
    except:
        flash("No points earned so far, cannot compute grade")
    return redirect(url_for('course',course_id=course_id))

####------- HELPER FUNCTIONS -------####
def course_average(course):
    return reduce(lambda total_avg,c: c.compute_average()+total_avg if c.compute_raw_total() > 0.0 else total_avg,course.categories,0.0)

def completed_categories_weight(course):
    return reduce(lambda weight,c: c.weight+weight if c.compute_raw_total() > 0.0 else weight, course.categories,0.0)

####--------------------------------####

if __name__ == "__main__":
    app.run()
