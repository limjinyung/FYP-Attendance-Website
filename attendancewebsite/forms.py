from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from attendancewebsite.models import Student, Staff
from attendancewebsite import db
from flask_login import current_user


class StudentRegistrationForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired()])
    DOB = DateField("Date of Birth", format='%d/%m/%Y', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
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


# class StudentSearchForm(FlaskForm, current_user):
#
#     def get_unit(check_unit):
#         units = []
#         for i in range(len(check_unit)):
#             if check_unit[i][1] not in units:
#                 units.append(check_unit[i][1])
#
#         return units
#
#     def generate_choices(units):
#         choices = []
#         for j in range(len(units)):
#             choices.append((units[j], units[j]))
#
#         return choices
#
#     print(current_user)
#     sid = ''
#     check_unit = db.session.query(student_unit).filter(student_unit.c.student_id == '29036186' ).all()
#     choices = generate_choices(get_unit(check_unit))
#     choose_unit = SelectField('Student Unit', choices=choices)
#     submit = SubmitField('Search')

