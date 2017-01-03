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

db.init_app(app)
lm = LoginManager()
lm.init_app(app)

def get_current_user():
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
    db.create_all()
    # initialize a default category so that users can populate all their grades first

@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    # Ensure unique usernames!
    if User.query.filter_by(username=request.form['username'].lower()).first() is not None:
        flash('That username is already taken')
        return redirect(url_for('register'))

    new_user = User(request.form['username'],request.form['password'])
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

        # Go to the next page specified in HTML or default show_semesters
        return redirect(request.args.get('next') or url_for('show_semesters'))
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

@app.route('/')
def show_semesters():
    """
    Show semesters for the logged-in user
    """
    # Current user is a global managed by LoginManager
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user is None:
        return redirect(url_for('login'))
    semesters = [semester for semester in user.semesters]
    return render_template('overview.html', semesters=semesters,user=user,form=SemesterForm())

@app.route('/add_semester', methods=['POST'])
@login_required
def add_semester():
    # TODO: separate form validation and object creation
    # semester = SemesterForm(request.POST,None)
    if request.form:
        f = SemesterForm(request.form)
        if f.validate():
            if Semester.query.filter_by(season=f.data['season'].upper(),year=f.data['year']).first() is None:
                db.session.add(Semester(f.data['season'].upper(),f.data['year'],f.data['user_id']))
                db.session.commit()
            else:
                flash('Semester already added')
        else:
            flash(f.errors)
    return redirect(url_for('show_semesters'))

@app.route('/semester')
@login_required
def semester():
    try:
        season = request.args.get('season')
        year = request.args.get('year')
    except:
        flash('Semester does not exist in the database')
        return redirect(url_for('show_semesters'))
    # TODO: show courses that exist for that semester
    semester = Semester.query.filter_by(season=season,year=year,user_id=get_current_user().id).first()
    if semester is None:
        flash('Could not find a semester associated with %s %s for %s' % (season,year,get_current_user().id))
        return redirect(url_for('show_semesters'))
    courses = [course for course in semester.courses]
    return render_template('semester.html', courses=courses,season=season,year=year,semester=semester,form=CourseForm())


@app.route('/semester/add_course', methods=['POST'])
@login_required
def add_course():
    if request.form:
        f = CourseForm(request.form)
        if f.validate():
            print request.form
            for key in request.form:
                print request.form[key]
            new_course = Course(f.data['name'],f.data['instructor'],f.data['semester_id'])
            db.session.add(new_course)
            db.session.commit()
            category_names = map(lambda key: request.form[key], filter(lambda kv: kv.startswith('category'),request.form))
            category_weights = map(lambda key: request.form[key],filter(lambda kv: kv.startswith('weight'),request.form))
            print category_names
            print category_weights
            for i in xrange(len(category_names)):
                new_category = Category(category_names[i],category_weights[i],new_course.id)
                db.session.add(new_category)
                db.session.commit()
            flash('Course added!')

        else:
            flash(f.errors)
    year = request.form['year']
    season = request.form['season']
    return redirect(url_for('semester', season=season, year=year))

@app.route('/course/<course_id>')
@login_required
def course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return redirect(url_for('show_semesters'))
    semester = Semester.query.filter_by(id=course.semester_id).first()
    course_avg = course_average(course)
    context = {
        'course' : course,
        'semester' : semester,
        'categories' : [category for category in Category.query.all()],
        'course_avg' : course_avg,
        'form' : CourseForm(),
    }
    return render_template('course.html',**context)

def course_average(course):
    return reduce(lambda total_avg,c: c.compute_average()+total_avg,course.categories,0.0)

@app.route('/course/<course_id>/add_grade', methods=['POST'])
@login_required
def add_grade(course_id):
    course = Course.query.filter_by(id=course_id).first()
    semester = Semester.query.filter_by(id=course.semester_id).first()
    #TODO: validate course_id and category_id!!!!
    assignment = Assignment(request.form['title'],
                            request.form['points_earned'],
                            request.form['total_points'],
                            request.form['category_id'])
    db.session.add(assignment)
    db.session.commit()
    return redirect(url_for('course', course_id=course_id))

@app.route('/category/<course_id>',methods=['GET'])
@login_required
def category(course_id):
    print 'helo'
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        flash('Course not found')
        return redirect(url_for('show_semesters'))
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
    return redirect(url_for('show_semesters'))

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

@app.route('/course/<course_id>/assignments/<assignment_id>/update', methods=['POST'])
@login_required
def update_assignment(course_id,assignment_id):
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if assignment is None:
        print 'hello'
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
    percent = course_average(course)
    flash("Grade for this course: %.2f %%" % (percent*100.0))
    if (percent*100.0) > 100.0:
        flash("Grade for this course is over 100%. Ensure that this is correct and that the category weights are valid.")
    return redirect(url_for('course',course_id=course_id))

if __name__ == "__main__":
    app.run()
