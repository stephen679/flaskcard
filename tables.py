from flask_table import Table, Col, NestedTableCol

class AssignmentTable(Table):
    name = Col('name')
    earned_points = Col('earned points')
    total_points = Col('total points')

class CategoryTable(Table):
    name = Col('name')
    weight = Col('weight')
    assignments = NestedTableCol('assignments',AssignmentTable)

class CourseTable(Table):
    name = Col('Course name')
    instructor = Col('Instructor')
    categories = NestedTableCol('Categories',CategoryTable)
