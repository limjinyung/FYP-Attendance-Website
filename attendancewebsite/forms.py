"""
FILENAME - forms.py
CODING - UTF-8
USAGE - Building forms using FlaskForm with own defined function to validate credentials like ID and email for student
        and staff while signing up.
DATE - Started Aug 9 2020
NOTES - Python version used is 3.7 and the database adapter used to connect with PostgreSQl is the psycopg binary
CODED BY - LIM JIN YUNG
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from attendancewebsite.models import Student, Staff


class StudentRegistrationForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired()])
    DOB = DateField("Date of Birth", format='%d/%m/%Y', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    uid = StringField('Student Card ID', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_id(self, student_id):
        if len(student_id) != 8:
            raise ValidationError("Please insert the id correctly")

        student = Student.query.filter_by(student_id=student_id.data).first()
        staff = Staff.query.filter_by(staff_id=student_id.data).first()
        if (student == student_id.data) or (staff == student_id.data):
            raise ValidationError('That id is taken. Please choose a different one.')

    def validate_email(self, email):
        email_data = email.data
        email_format = email_data.split("@", 1)[1]
        if email_format != "student.monash.edu":
            raise ValidationError('Email format incorrect. Please try again.')

        student = Student.query.filter_by(email=email.data).first()
        if (student==email_data):
            raise ValidationError('That email is taken. Please choose a different one.')


class StaffRegistrationForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    DOB = DateField("Date of Birth", format='%d/%m/%Y', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_id(self, staff_id):
        if len(staff_id) != 8:
            raise ValidationError("Please insert the id correctly")

        student = Student.query.filter_by(student_id=staff_id.data).first()
        staff = Staff.query.filter_by(staff_id=staff_id.data).first()
        if (student==staff_id.data) or (staff==staff_id.data):
            raise ValidationError('That id is taken. Please choose a different one.')

    def validate_email(self, email):
        email_data = email.data
        email_format = email_data.split("@", 1)[1]
        if email_format != "staff.monash.edu":
            raise ValidationError('Email format incorrect. Please try again.')

        staff = Staff.query.filter_by(email=email.data).first()
        if staff:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

