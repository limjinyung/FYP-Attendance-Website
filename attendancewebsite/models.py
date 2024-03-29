"""
FILENAME - models.py
CODING - UTF-8
USAGE - Creates database model using class modal where each column will have own specified data type, primary key,
        foreign key. Database model can be built directly from python console by running the command db.create_all()
DATE - Started Aug 9 2020
NOTES - Python version used is 3.7 and the database adapter used to connect with PostgreSQl is the psycopg binary
CODED BY - LIM JIN YUNG
"""

from attendancewebsite import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    id = user_id.split('.')
    try:
        uid = id[1]
        if id[0] == 'student':
            return Student.query.get(uid)
        elif id[0] == 'staff':
            return Staff.query.get(uid)
        else:
            raise ValueError('No ID is found')
    except IndexError:
        return None


class Student(db.Model, UserMixin):
    student_id = db.Column(db.String(8), primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    DOB = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    uid = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return "Student('" + str(self.student_id) + ', ' + self.last_name + ', ' + self.first_name + ', ' + self.email + "')"

    def get_id(self):
        return 'student.' + self.student_id


class Staff(db.Model, UserMixin):
    staff_id = db.Column(db.String(8), primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    DOB = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return "Staff('" + str(self.staff_id) + ', ' + self.last_name + ', ' + self.first_name + ', ' + self.email  + "')"

    def get_id(self):
        return 'staff.' + self.staff_id


class Unit(db.Model):
    unit_code = db.Column(db.String(20), primary_key=True)
    unit_name = db.Column(db.String(120), unique=True, nullable=False)
    unit_offer = db.Column(db.Boolean, nullable=False)

    def __init__(self, unit_code, unit_name, unit_offer):
        self.unit_code = unit_code
        self.unit_name = unit_name
        self.unit_offer = unit_offer

    def __repr__(self):
        return "Unit('" + self.unit_code + ' ' + self.unit_name + ' ' + self.unit_offer + "')"


class Room(db.Model):
    room_id = db.Column(db.String(15), primary_key=True)

    def __init__(self, room_id):
        self.room_id = room_id

    def __repr__(self):
        return "Room('" + self.room_id + "')"


class Semester(db.Model):
    year = db.Column(db.String(10), primary_key=True)
    semester = db.Column(db.String(1), primary_key=True)
    start_date = db.Column(db.String(10), primary_key=True)
    week_before_sembreak = db.Column(db.Integer)

    def __init__(self, year, semester,  start_date):
        self.year = year
        self.semester = semester
        self.start_date = start_date

    def __repr__(self):
        return "Semester('" + self.year + ', ' + self.semester + ',' + str(self.start_date) + "')"


class Club(db.Model):
    club_code = db.Column(db.String(30), primary_key=True, unique=True, nullable=False)
    club_name = db.Column(db.String(30), primary_key=True, nullable=False)
    club_start_time = db.Column(db.Time, primary_key=True, nullable=False)
    day = db.Column(db.String(10), primary_key=True, nullable=False)
    club_duration = db.Column(db.Integer, nullable=False)


class Weather(db.Model):
    unit_code = db.Column(db.String(20), primary_key=True)
    week = db.Column(db.Integer, primary_key=True)
    class_datetime = db.Column(db.DateTime, nullable=False)
    year = db.Column(db.String(10), primary_key=True)
    semester = db.Column(db.String(1), primary_key=True)
    weather = db.Column(db.String(20), nullable=False)


# Association tables


student_unit = db.Table('student_unit',
            db.Column('student_id', db.String(8), db.ForeignKey('student.student_id'), primary_key=True),
            db.Column('unit_code', db.String(20), db.ForeignKey('unit.unit_code'), primary_key=True),
            db.Column('year', db.String(10), primary_key = True),
            db.Column('semester', db.String(1), primary_key = True),
)

attendance = db.Table('attendance',
            db.Column('student_id', db.String(8), db.ForeignKey('student.student_id'), primary_key=True),
            db.Column('unit_code', db.String(20), db.ForeignKey('unit.unit_code'), primary_key=True),
            db.Column('week', db.Integer, primary_key=True),
            db.Column('time_in', db.DateTime),
            db.Column('time_out', db.DateTime),
            db.Column('late', db.Boolean),
            db.Column('year', db.String(10)),
            db.Column('semester', db.String(1)),
)


staff_unit = db.Table('staff_unit',
            db.Column('staff_id', db.String(8), db.ForeignKey('staff.staff_id'), primary_key=True),
            db.Column('unit_code', db.String(20), db.ForeignKey('unit.unit_code'), primary_key=True),
)


room_unit = db.Table('room_unit',
            db.Column('room_id', db.String(10), db.ForeignKey('room.room_id'), primary_key=True),
            db.Column('unit_code', db.String(20), db.ForeignKey('unit.unit_code'), primary_key=True),
            db.Column('class_start_time', db.Time, primary_key=True),
            db.Column('class_duration', db.Integer),
            db.Column('day', db.String(10), primary_key=True),
)

student_club = db.Table('student_club',
            db.Column('student_id', db.String(8), db.ForeignKey('student.student_id'), primary_key=True),
            db.Column('club_code', db.String(30), db.ForeignKey('club.club_code'), primary_key=True),
)