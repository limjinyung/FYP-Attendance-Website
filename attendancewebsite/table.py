from flask_table import Table, Col
from attendancewebsite import db
from attendancewebsite.models import Student, Unit, attendance
from flask_login import  current_user


class StudentTable(Table):
    classes = ['table', 'table-striped', 'table-bordered', 'table-hovered']
    unit_code = Col('Unit Code')
    time_in = Col('Time In')
    time_out = Col('Time Out')
    late = Col('Late')
    year = Col('Year')
    semester = Col('Semester')


class Item(object):
    def __init__(self, unit_code, time_in, time_out, late, year, semester):
        self.unit_code = unit_code
        self.time_in = time_in
        self.time_out = time_out
        self.late = late
        self.year = year
        self.semester = semester

check_student_id = '29036186'
check_unit_code = 'FIT3155_L1'

student_attendance = db.session.query(attendance).filter(attendance.c.student_id==check_student_id)

student_table = StudentTable(student_attendance)
