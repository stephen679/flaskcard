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
	course TEXT NOT NULL,
	FOREIGN KEY(course) REFERENCES courses(name)
);


DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
	name TEXT NOT NULL,
	instructor TEXT
);

DROP TABLE IF EXISTS assignment;
CREATE TABLE assignment (
	title TEXT,
	unweighted_grade REAL,
	course TEXT NOT NULL,
	category TEXT NOT NULL,
	FOREIGN KEY(course) REFERENCES courses(name),
	FOREIGN KEY(category) REFERENCES categories(name)
);
