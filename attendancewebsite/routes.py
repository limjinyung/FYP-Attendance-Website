from flask import render_template, url_for, flash, redirect, request, session, make_response
from attendancewebsite import app, db, bcrypt
from attendancewebsite.forms import LoginForm, StudentRegistrationForm, StaffRegistrationForm
from attendancewebsite.models import Student, Staff, attendance, student_unit
from flask_login import login_user, current_user, logout_user
from io import StringIO
import csv
from attendancewebsite.service import get_unit, create_attendance_sheet, generate_attendance_total_percentage, \
    generate_attendance_percentage, sort_unit, extract_units, calculate_unit_attendance, this_year, this_semester, \
    extract_student_id


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.email.split("@", 1)[1] == 'student.monash.edu':
            return redirect(url_for('student_page'))
        elif current_user.email.split("@", 1)[1] == 'staff.monash.edu':
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
        if current_user.email.split("@", 1)[1] == 'student.monash.edu':
            return redirect(url_for('student_page'))
        elif current_user.email.split("@", 1)[1] == 'staff.monash.edu':
            return redirect(url_for('staff_page'))
    return render_template('index.html', title="Home")


@app.route('/student_page', methods=['GET', 'POST'])
def student_page():

    # get attendance
    attendance_list = db.session.query(attendance).filter(attendance.c.student_id == current_user.student_id).\
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
        print(attendance_list, selected_units)
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

    # get the percentage of student attendance, e.g. {'FIT3081_L1': [100.00, 100.00, 90.00,...],
    # 'FIT3155_T1': [100.00, 100.00, 80.00,...]
    attendance_percentage = generate_attendance_percentage(attendance_sheet[0], student_attendance_week_list)

    # get the total percentage of student attendance, e.g. {'FIT3081_L1': 100.0, 'FIT3081_T1': 80.0,
    # 'FIT3155_L1': 40.0, 'FIT3155_T1': 60.0}
    attendance_table = generate_attendance_total_percentage(attendance_sheet[0], student_attendance_week_list)

    return render_template('student_page.html', title='Student Page', choices=choose_units, weeks=attendance_sheet[1],
                           python_dict=attendance_percentage, table=attendance_table)


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
        student_details = db.session.query(Student).filter(Student.student_id == sid).first()
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

        student_attendance_percentage = generate_attendance_total_percentage(attendance_sheet[0],
                                                                             student_attendance_week_list)

        return render_template('staff_student_attendance.html', title='Student Attendance Page',
                               student_attendance_dict=student_attendance_percentage,
                               student_details_id=student_details_id,
                               student_details_fn=student_details_first_name,
                               student_details_ln=student_details_last_name)

    else:

        flash('Please enter a student id to view student attendance', 'info')
        return render_template('staff_student_attendance.html',
                               title='Student Attendance Page', student_attendance_dict={})


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
                                   unit_attendance_percentage=unit_attendance_percentage,
                                   week_list=attendance_sheet[1], uid=uid)

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
        student_details = db.session.query(Student).filter(Student.student_id == sid).first()
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