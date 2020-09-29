from flask import render_template, url_for, flash, redirect, request, session, make_response
from attendancewebsite import app, db, bcrypt
from attendancewebsite.forms import LoginForm, StudentRegistrationForm, StaffRegistrationForm
from attendancewebsite.models import Student, Staff, Semester, Unit, attendance, student_unit
from flask_login import login_user, current_user, logout_user
from io import StringIO
import csv
from datetime import datetime, timedelta
from flask_socketio import SocketIO

# start_week = datetime(2020, 8, 3)
# this_year = '2020'
# this_semester = '2'
week_length = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

start_week = db.session.query(Semester.start_date).order_by(Semester.start_date.desc()).first()
this_year = db.session.query(Semester.year).order_by(Semester.start_date.desc()).first()
this_semester = db.session.query(Semester.semester).order_by(Semester.start_date.desc()).first()
start_week = datetime.strptime(start_week[0], '%Y-%m-%d').date()


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.email.split("@",1)[1] == 'student.monash.edu':
            return redirect(url_for('student_page'))
        elif current_user.email.split("@",1)[1] == 'staff.monash.edu':
            return redirect(url_for('staff_page'))
    form = LoginForm()
    redirect(url_for('login'))
    if form.validate_on_submit():
        email_data = form.email.data
        email_format = email_data.split("@", 1)[1]
        if email_format == "student.monash.edu":
            student = Student.query.filter_by(email=form.email.data).first()
            if student and bcrypt.check_password_hash(student.password, form.password.data):
                login_user(student, remember=form.remember.data)
                return redirect(url_for('student_page'))
            else:
                flash('Login Unsuccessful. Please check your password', 'danger')
        elif email_format == "staff.monash.edu":
            staff = Staff.query.filter_by(email=form.email.data).first()
            if staff and bcrypt.check_password_hash(staff.password, form.password.data):
                login_user(staff, remember=form.remember.data)
                return redirect(url_for('staff_page'))
            else:
                flash('Login Unsuccessful. Please check your password', 'danger')
        else:
            flash('Login Unsuccessful. Please check your email', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/student_register", methods=['GET', 'POST'])
def student_register():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        student = Student(student_id=form.student_id.data, first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, DOB=form.DOB.data, password=hashed_password)
        db.session.add(student)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('student_register.html', title='Register', form=form)


@app.route("/staff_register", methods=['GET', 'POST'])
def staff_register():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = StaffRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        staff = Staff(staff_id=form.staff_id.data, first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, DOB=form.DOB.data, password=hashed_password)
        db.session.add(staff)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('staff_register.html', title='Register', form=form)


@app.route('/')
@app.route("/index", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        if current_user.email.split("@",1)[1] == 'student.monash.edu':
            return redirect(url_for('student_page'))
        elif current_user.email.split("@",1)[1] == 'staff.monash.edu':
            return redirect(url_for('staff_page'))
    return render_template('index.html', title="Home")


def get_unit(attendance_list):

        units = []

        for i in range(len(attendance_list)):
            if attendance_list[i][1] not in units:
                units.append(attendance_list[i][1])

        return units


def create_attendance_sheet():
    week_list = []

    for i in range(12):
        week_list.append(start_week + timedelta(days=(7*i)))

    this_week = 0
    today_str = datetime.today().strftime('%Y-%m-%d')
    today = datetime.strptime(today_str, '%Y-%m-%d').date()

    for j in range(len(week_list)):
        if j == 0:
            if (today == week_list[j]) or (today < week_list[j + 1]):
                this_week = j + 1
                break
        else:
            if (today == week_list[j]) or (week_list[j - 1] < today < week_list[j + 1]):
                this_week = j + 1
                break

    check_attendance_sheet = []
    for k in range(len(week_list[0:this_week])):
        check_attendance_sheet.append(k+1)

    chart_week_display = []
    for l in range(len(check_attendance_sheet)):
        chart_week_display.append("W" + str(check_attendance_sheet[l]))

    return check_attendance_sheet, chart_week_display


def generate_attendance_percentage(attendance_sheet, student_attendance_week_list):

    student_attendance_percentage = {}

    for key in student_attendance_week_list:

        mark_attendance = []
        mark_attendance_percentage = []

        for i in range(1, len(attendance_sheet)+1):

            if i in student_attendance_week_list[key]:
                mark_attendance.append(i)

            count_percentage = (len(mark_attendance) / len(attendance_sheet[0:i])) * 100

            mark_attendance_percentage.append(count_percentage)

        student_attendance_percentage[key] = mark_attendance_percentage

    return student_attendance_percentage


def student_attendance_week(attendance_list):
    """
    take attendance list and extract the 'week' column
    :param attendance_list: attendance list from database
    :return: an array consist only weeks that have been attended by the student
    """

    student_attendance = []
    for i in range(len(attendance_list)):
        student_attendance.append(attendance_list[i][2])

    return student_attendance


def sort_unit(units, attendance_list):

    student_attendance = {}

    for i in range(len(units)):
        student_attendance[units[i]] = []

    for j in range(len(attendance_list)):
        if attendance_list[j][1] in student_attendance:
            student_attendance[attendance_list[j][1]].append(attendance_list[j][2])

        student_attendance[attendance_list[j][1]].sort()

    return student_attendance


def extract_units(attendance_list, selected_units):

    for i in range(len(attendance_list)):

      if attendance_list[i][1] not in selected_units:
        attendance_list[i] = '-'

    count = 0
    while count != (len(attendance_list)):

        if attendance_list[count] == '-':
            attendance_list.pop(count)
            continue
        else:
            count += 1

    return attendance_list


def generate_attendance_total_percentage(attendance_sheet, student_attendance_week_list):

    student_attendance_percentage = {}

    for key in student_attendance_week_list:

        student_attendance_percentage[key] = (len(student_attendance_week_list[key]) / len(attendance_sheet)) * 100

    return student_attendance_percentage


@app.route('/student_page', methods=['GET', 'POST'])
def student_page():

    # get attendance
    attendance_list = db.session.query(attendance).filter(attendance.c.student_id == current_user.student_id ).\
        filter(attendance.c.year == this_year).\
        filter(attendance.c.semester == this_semester).all()

    # from student_unit get student's all unit
    unit_list = db.session.query(student_unit).filter(student_unit.c.student_id == current_user.student_id). \
        filter(attendance.c.year == this_year). \
        filter(attendance.c.semester == this_semester).all()

    # if the request method is POST
    # get the value from checkbox and query the database
    if request.method == "POST":
        selected_units = request.form.getlist("choose_unit")
        if selected_units == []:
            flash('Please at least tick one unit!', 'danger')
        choose_units = get_unit(attendance_list)
        attendance_list = extract_units(attendance_list, selected_units)
    # else if the request method is GET
    # query all unit value
    else:
        # get units, e.g. ['FIT3091_L1', 'FIT3155_T2']
        selected_units = get_unit(attendance_list)
        choose_units = get_unit(attendance_list)

    # get the week list, e.g. [1,2,3,4...]
    attendance_sheet = create_attendance_sheet()

    # sort the unit accordingly
    # e.g. {'FIT3081_L1': [1, 2, 3, 4], 'FIT3081_T1': [1, 2, 3, 4],...}
    student_attendance_week_list = sort_unit(selected_units, attendance_list)

    # get the percentage of student attendance, e.g. {'FIT3081_L1': [100.00, 100.00, 90.00,...], 'FIT3155_T1': [100.00, 100.00, 80.00,...]
    attendance_percentage = generate_attendance_percentage(attendance_sheet[0], student_attendance_week_list)

    # get the total percentage of student attendance, e.g. {'FIT3081_L1': 100.0, 'FIT3081_T1': 80.0, 'FIT3155_L1': 40.0, 'FIT3155_T1': 60.0}
    attendance_table = generate_attendance_total_percentage(attendance_sheet[0], student_attendance_week_list)

    return render_template('student_page.html', title='Student Page', choices=choose_units, weeks=attendance_sheet[1], python_dict=attendance_percentage, table=attendance_table)


def extract_student_id(attendance_list):

    table_data = []

    for i in range(len(attendance_list)):
        table_col = []
        for j in range(1, len(attendance_list[i])):
            table_col.append(attendance_list[i][j])
        table_data.append(table_col)

    return table_data


@app.route('/student_attendance_data_page', methods=['GET', 'POST'])
def student_attendance_data_page():

    # get attendance
    attendance_list = db.session.query(attendance).filter(attendance.c.student_id == current_user.student_id). \
        filter(attendance.c.year == this_year). \
        filter(attendance.c.semester == this_semester).order_by(attendance.c.week).all()

    table_data = extract_student_id(attendance_list)

    return render_template('student_attendance_data_page.html', title='Student Page', table=table_data)


@app.route('/student_download_attendance', methods=['POST'])
def download_student_csv():
    if request.method == 'POST':
        attendance_list = db.session.query(attendance).filter(
            attendance.c.student_id == current_user.student_id).all()
        si = StringIO()
        cw = csv.writer(si)
        cw.writerows(attendance_list)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=attendance_list.csv"
        output.headers["Content-type"] = "text/csv"
        return output


@app.route('/staff_page', methods=['GET', 'POST'])
def staff_page():
    return render_template('staff_page.html', title='Student Page')


@app.route('/staff_student_attendance', methods=['GET', 'POST'])
def staff_student_attendance():

    if request.method == "POST":
        sid = request.form.get("search_sid")

        # get the student details
        student_details = db.session.query(Student).filter(Student.student_id==sid).first()
        student_details_id = student_details.student_id
        student_details_first_name = student_details.first_name
        student_details_last_name = student_details.last_name

        # get the attendance of the student
        attendance_list = db.session.query(attendance).filter(attendance.c.student_id == sid). \
            filter(attendance.c.year == this_year). \
            filter(attendance.c.semester == this_semester).all()

        # get the week list, e.g. [1,2,3,4...]
        attendance_sheet = create_attendance_sheet()

        # get the student's unit list, e.g. ['FIT3091_L1', 'FIT3155_T2']
        student_unit_list = get_unit(attendance_list)

        # sort the unit accordingly
        # e.g. {'FIT3081_L1': [1, 2, 3, 4], 'FIT3081_T1': [1, 2, 3, 4],...}
        student_attendance_week_list = sort_unit(student_unit_list, attendance_list)

        student_attendance_percentage = generate_attendance_total_percentage(attendance_sheet[0], student_attendance_week_list)

        return render_template('staff_student_attendance.html', title='Student Attendance Page', student_attendance_dict=student_attendance_percentage, student_details_id=student_details_id, student_details_fn=student_details_first_name, student_details_ln=student_details_last_name)

    else:

        flash('Please enter a student id to view student attendance', 'info')
        return render_template('staff_student_attendance.html', title='Student Attendance Page', student_attendance_dict={})


def calculate_unit_attendance(attendance_list, unit_code):

    # get all the students that are taking the unit
    # e.g. [('29036186', 'FIT3155_L1', '2020', '2'), ('29821894', 'FIT3155_L1', '2020', '2'), ...]
    student_list = db.session.query(student_unit).filter(student_unit.c.unit_code == unit_code).filter(
        student_unit.c.year == this_year).filter(student_unit.c.semester == this_semester).all()

    total_attendance_number = len(student_list)

    unit_attendance = {}

    for i in range(len(attendance_list)):

        if attendance_list[i][2] in unit_attendance:
            unit_attendance[attendance_list[i][2]] += 1
        else:
            unit_attendance[attendance_list[i][2]] = 1

    for week in unit_attendance:

        unit_attendance[week] = (unit_attendance[week]/total_attendance_number)*100

    return unit_attendance


@app.route('/staff_unit_attendance', methods=['GET', 'POST'])
def staff_unit_attendance():

    if request.method == "POST":
        uid = request.form.get("search_uid")

        # get the attendance of the unit
        attendance_list = db.session.query(attendance).filter(attendance.c.unit_code == uid). \
            filter(attendance.c.year == this_year). \
            filter(attendance.c.semester == this_semester).all()

        if attendance_list:

            unit_attendance_percentage = calculate_unit_attendance(attendance_list, uid)

            # get the week list, e.g. [1,2,3,4...]
            attendance_sheet = create_attendance_sheet()

            return render_template('staff_unit_attendance.html', title='Unit Attendance Page',
                               unit_attendance_percentage=unit_attendance_percentage, week_list=attendance_sheet[1], uid=uid)

        else:

            # get the week list, e.g. [1,2,3,4...]
            attendance_sheet = create_attendance_sheet()

            flash('Please enter a valid unit code.', 'danger')
            return render_template('staff_unit_attendance.html', title='Unit Attendance Page',
                                   unit_attendance_percentage={}, week_list=attendance_sheet[1], uid="")

    else:

        # get the week list, e.g. [1,2,3,4...]
        attendance_sheet = create_attendance_sheet()

        return render_template('staff_unit_attendance.html', title='Unit Attendance Page',
                           unit_attendance_percentage={}, week_list=attendance_sheet[1], uid="")


@app.route('/late_absent_page', methods=['GET', 'POST'])
def late_absent_page():

    if request.method == "POST":
        uid = request.form.get("search_uid")
        sid = request.form.get("search_sid")

        if uid and sid:
            attendance_list = db.session.query(attendance).filter(attendance.c.unit_code == uid). \
                filter(attendance.c.student_id == sid). \
                filter(attendance.c.year == this_year). \
                filter(attendance.c.semester == this_semester).all()

            print(attendance_list)
        elif not uid and not sid:
            flash("Please enter full information", "danger")
            return render_template('late_absent_page.html', title='Late Absent Page')
        elif not sid:
            flash("Please enter student id", "danger")
            return render_template('late_absent_page.html', title='Late Absent Page')
        else:
            flash("Please enter unit code", "danger")
            return render_template('late_absent_page.html', title='Late Absent Page')

    return render_template('late_absent_page.html', title='Late Absent Page')


@app.route('/attendance_data_page', methods=['GET', 'POST'])
def attendance_data_page():

    if request.method == "POST":
        sid = request.form.get("search_sid")

        # get the student details
        student_details = db.session.query(Student).filter(Student.student_id==sid).first()
        student_details_id = student_details.student_id
        student_details_first_name = student_details.first_name
        student_details_last_name = student_details.last_name

        # get the attendance of the student
        attendance_list = db.session.query(attendance).filter(attendance.c.student_id == sid). \
            filter(attendance.c.year == this_year). \
            filter(attendance.c.semester == this_semester).all()

        # get the student's unit list, e.g. ['FIT3091_L1', 'FIT3155_T2']
        student_unit_list = get_unit(attendance_list)

    return render_template('attendance_data_page.html', title='Attendance Data Page')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.before_request
def make_session_permanent():
    session.permanent = False