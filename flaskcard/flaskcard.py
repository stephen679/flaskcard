# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user , logout_user , current_user , login_required
from contextlib import closing # helps initialize a database so we don't have to hardcode
from models import *

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'development key'
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = 'default'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/flaskcard.db'

db.init_app(app)
lm = LoginManager()
lm.init_app(app)


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
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
        registered_user = User.query.filter_by(username=username,password=password).first()
        if registered_user is None:
            flash('Username or Password is invalid' , 'error')
            return redirect(url_for('login'))
        login_user(registered_user)
        flash('You\'re logged in')
        return redirect(request.args.get('next') or url_for('show_semesters'))
    return render_template('login.html', error=err)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out')
    return redirect(url_for('login'))

@app.before_request
def before_request():
    g.user = current_user

@app.before_first_request
def initialize_database():
    db.create_all()

@app.route('/')
def show_semesters():
    semesters = [semester for semester in Semester.query.all()]
    return render_template('overview.html', semesters=semesters)

@app.route('/add_semester', methods=['POST'])
def add_semester():
    semester = Semester(request.form['season'],request.form['year'],current_user.get_id())
    db.session.add(semester)
    db.session.commit()
    flash('Semester has been added!')
    return redirect(url_for('show_semesters'))


@app.route('/semester')
def semester():
    try:
        season = request.args.get('season')
        year = request.args.get('year')
    except:
        return redirect(url_for('show_semesters'))
    # TODO: show courses that exist for that semester
    cur = g.db.execute('SELECT * FROM courses')
    courses = [dict(name=row[0], instructor=row[1]) for row in cur.fetchall()]
    print courses
    return render_template('semester.html', courses=courses,season=season,year=year)


@app.route('/semester/add_course', methods=['POST'])
def add_course():
    if not session.get('logged_in'):
        abort(401)
    try:
        g.db.execute('INSERT INTO courses (name,instructor) VALUES (?,?)', [request.form['course_name'],request.form['instructor']])
    except:
        flash('that course has already been added')
    else:
        g.db.commit()
        flash('Course added!')
    year = request.form['year']
    season = request.form['season']
    return redirect(url_for('semester', season=season, year=year))

@app.route('/course/<name>')
def course(name):
    cur = g.db.execute('SELECT * FROM assignment WHERE course = ' + str(name))
    assignments = []
    for row in cur.fetchall():
        attributes = dict()
        attributes['title'] = row[0]
        attributes['unweighted_grade'] = row[1]
        attributes['course'] = row[2]
        attributes['category'] = row[3]
        assignments.append(attributes)
    return render_template('course.html', assignments=assignments)

@app.route('/course/<name>/add_grade', methods=['POST'])
def add_grade():
    if not session.get('logged_in'):
        abort(401)
    try:
        f = request.form
        g.db.execute('INSERT INTO assignment (title,unweighted_grade,course,category) VALUES (?,?,?,?)',
                        [f['title'], f['unweighted_grade'], f['course'], f['category']])
    except:
        # todo: assignments should be able to be updated
        flash('assignment already added')
    else:
        g.db.commit()
        flash('Assignment added ~~')
    return redirect(url_for('course',name=f['course]']))

# running the app by itself from command line
if __name__ == "__main__":
    app.run()
