DROP TABLE IF EXISTS users;
CREATE TABLE users (
	username TEXT NOT NULL,
	password TEXT NOT NULL,
	email_address TEXT,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	reportcard semesters
);

DROP TABLE IF EXISTS semesters;
CREATE TABLE semesters (
	year INTEGER NOT NULL,
	season TEXT NOT NULL,
	schedule courses,
	PRIMARY KEY(season, year)
);

DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
	name TEXT NOT NULL,
	weight REAL NOT NULL,
	course_name TEXT NOT NULL,
	FOREIGN KEY(course_name) REFERENCES courses(name)
);


DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
	name TEXT NOT NULL,
	instructor TEXT,
	report assignments
);

DROP TABLE IF EXISTS assignment;
CREATE TABLE assignments (
	title TEXT,
	unweighted_grade REAL,
	course_name TEXT NOT NULL,
	category_name TEXT NOT NULL,
	FOREIGN KEY(course_name) REFERENCES courses(name),
	FOREIGN KEY(category_name) REFERENCES categories(name)
);
