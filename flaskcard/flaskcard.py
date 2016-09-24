# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from contextlib import closing # helps initialize a database so we don't have to hardcode
from models import *

app = Flask(__name__)

# configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/flaskcard.db'
app.config['DATABASE'] = '/tmp/flaskcard.db' # eventually change this to get these items from environment
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'development key'
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = 'default'

db = SQLAlchemy(app)

# user can set environment variable FLASKCARD_SETTINGS to a path for a config file
# app.config.from_envvar("FLASKCARD_SETTINGS", silent=True)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.route('/')
def show_semesters():
	cur = g.db.execute('SELECT * FROM semesters')
	semesters = [dict(year=row[0], season=row[1]) for row in cur.fetchall()]
	return render_template('overview.html', semesters=semesters)

@app.route('/add_semester', methods=['POST'])
def add_semester():
	if not session.get('logged_in'):
		abort(401) # only a logged-in user can create a semester
	try:
        # TODO: add semester
		g.db.execute('INSERT INTO semesters (year,season) VALUES (?,?)', [request.form['year'],request.form['season']])
	except:
		flash('that semester has been created already >:(')
	else:
		g.db.commit()
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

@app.route('/login', methods=['GET', 'POST'])
def login():
	err = None
	if request.method == "POST":
		if request.form['username'] != app.config['USERNAME']:
			err = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			err = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You\'re logged in')
			return redirect(url_for('show_semesters'))
	return render_template('login.html', error=err)

@app.route('/logout')
def logout():
	session.pop('logged_in',None)
	flash('You logged out')
	return redirect(url_for('show_semesters'))

# running the app by itself from command line
if __name__ == "__main__":
	app.run()
