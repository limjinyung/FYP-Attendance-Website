"""
FILENAME - routes.py
CODING - UTF-8
USAGE - Map all URLs to actions such as displaying charts, table, perform analysis by calling functions from the file
        service.py all HTTP errors all handled by the function handle_error.
DATE - Started Aug 9 2020
NOTES - Python version used is 3.7 and the database adapter used to connect with PostgreSQl is the psycopg binary
CODED BY - LIM JIN YUNG
"""

from flask import render_template, url_for, flash, redirect, request, session, make_response
from attendancewebsite import app, db, bcrypt
from attendancewebsite.forms import LoginForm, StudentRegistrationForm, StaffRegistrationForm
from attendancewebsite.models import Student, Staff, Semester, Unit, Club, Weather, attendance, student_unit, room_unit, student_club
from flask_login import login_user, current_user, logout_user, login_required
from io import StringIO
from datetime import datetime
import csv
from attendancewebsite.service import get_unit, create_attendance_sheet, generate_attendance_total_percentage, \
    generate_attendance_percentage, sort_unit, extract_units, calculate_unit_attendance, \
    attendance_data_without_sid, calculate_absent_data, calculate_late_data, analysis_algo

# week length will be set here in case of anything the week length need to be changed
# it'll be easy to just change it here
week_length = 12

start_week = db.session.query(Semester.start_date).order_by(Semester.start_date.desc()).first()
this_year = db.session.query(Semester.year).order_by(Semester.start_date.desc()).first()
this_semester = db.session.query(Semester.semester).order_by(Semester.start_date.desc()).first()
semester_break = db.session.query(Semester.week_before_sembreak).order_by(Semester.start_date.desc()).first()
week_before_semester = semester_break[0]
start_week = datetime.strptime(start_week[0], '%Y-%m-%d')

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
        student = Student(student_id=form.student_id.data, first_name=form.first_name.data,
                          last_name=form.last_name.data, email=form.email.data,
                          DOB=form.DOB.data, password=hashed_password, uid=form.uid.data)
        db.session.add(student)
        db.session.commit()
        flash('Please wait admin to confirm your account before you can login', 'success')
        return redirect(url_for('login'))
    return render_template('student_register.html', title='Register', form=form)


@app.route("/staff_register", methods=['GET', 'POST'])
def staff_register():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = StaffRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        staff = Staff(staff_id=form.staff_id.data, first_name=form.first_name.data, last_name=form.last_name.data,
                      email=form.email.data, DOB=form.DOB.data, password=hashed_password)
        db.session.add(staff)
        db.session.commit()
        flash('Please wait admin to confirm your account before you can login', 'success')
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
@login_required
def student_page():
    # get attendance
    attendance_list = db.session.query(attendance).filter(attendance.c.student_id == current_user.student_id). \
        filter(attendance.c.year == this_year[0]). \
        filter(attendance.c.semester == this_semester[0]).all()

    # from student_unit get student's all unit
    unit_list = db.session.query(student_unit).filter(student_unit.c.student_id == current_user.student_id). \
        filter(student_unit.c.year == this_year[0]). \
        filter(student_unit.c.semester == this_semester[0]).all()

    # if the request method is POST
    # get the value from checkbox and query the database
    if request.method == "POST":
        selected_units = request.form.getlist("choose_unit")
        if not selected_units:
            flash('Please tick at least one unit!', 'danger')
        choose_units = get_unit(unit_list)
        attendance_list = extract_units(attendance_list, selected_units)
    # else if the request method is GET
    # query all unit value
    else:
        # get units, e.g. ['FIT3091_L1', 'FIT3155_T2']
        selected_units = get_unit(unit_list)
        choose_units = get_unit(unit_list)

    # get the week list, e.g. [1,2,3,4...]
    attendance_sheet = create_attendance_sheet(start_week, week_before_semester)

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
@login_required
def student_attendance_data_page():
    # get attendance
    attendance_list = db.session.query(attendance).filter(attendance.c.student_id == current_user.student_id). \
        filter(attendance.c.year == this_year). \
        filter(attendance.c.semester == this_semester).order_by(attendance.c.week).all()

    table_data = attendance_data_without_sid(attendance_list)

    return render_template('student_attendance_data_page.html', title='Attendance Data Page', table=table_data)


@app.route('/student_download_attendance', methods=['POST'])
@login_required
def download_student_csv():
    if request.method == 'POST':
        attendance_list = db.session.query(attendance).filter(
            attendance.c.student_id == current_user.student_id).all()
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow([('Student ID'), ('Unit'), ('Week'), ('Time In'), ('Time Out'), ('Late'), ('Year'), ('Semester')])
        cw.writerows(attendance_list)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=" + str(
            current_user.student_id) + "_attendance_list.csv"
        output.headers["Content-type"] = "text/csv"
        return output


@app.route('/staff_page', methods=['GET', 'POST'])
@login_required
def staff_page():
    if is_staff(current_user):
        return render_template('staff_page.html', title='Staff Page')


@app.route('/staff_student_attendance', methods=['GET', 'POST'])
@login_required
def staff_student_attendance():
    if is_staff(current_user):

        if request.method == "POST":
            sid = request.form.get("search_sid")

            if sid == "":
                flash('Please at least enter a student id', 'danger')
                return render_template('staff_student_attendance.html',
                                       title='Student Attendance Page', student_attendance_dict={})

            try:
                # get the student details
                student_details = db.session.query(Student).filter(Student.student_id == sid).first()
                student_details_id = student_details.student_id
                student_details_first_name = student_details.first_name
                student_details_last_name = student_details.last_name

                # get the student's unit
                student_unit_in_database = db.session.query(student_unit).filter(student_unit.c.student_id == sid,
                                                                                 student_unit.c.year == this_year,
                                                                                 student_unit.c.semester == this_semester).all()


            except AttributeError:
                flash('Please enter a valid student id', 'danger')
                return render_template('staff_student_attendance.html',
                                       title='Student Attendance Page', student_attendance_dict={})

            # get the attendance of the student
            attendance_list = db.session.query(attendance).filter(attendance.c.student_id == sid). \
                filter(attendance.c.year == this_year). \
                filter(attendance.c.semester == this_semester).all()

            # get the week list, e.g. [1,2,3,4...]
            attendance_sheet = create_attendance_sheet(start_week, week_before_semester)

            # get the student's unit list, e.g. ['FIT3091_L1', 'FIT3155_T2']
            student_unit_list = get_unit(student_unit_in_database)

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
            flash('Please enter a student id to view student attendance, etc: 29036186', 'info')
            return render_template('staff_student_attendance.html',
                                   title='Student Attendance Page', student_attendance_dict={})


@app.route('/staff_unit_attendance', methods=['GET', 'POST'])
@login_required
def staff_unit_attendance():
    if is_staff(current_user):

        if request.method == "POST":
            uid = request.form.get("search_uid")

            if uid == "":
                flash('Please at least enter a unit code.', 'danger')
                return render_template('staff_unit_attendance.html', title='Unit Attendance Page',
                                       unit_attendance_percentage={}, week_list=[], uid="")

            uid = uid.upper()
            uid = ' '.join(uid.split())

            # get the week list, e.g. [1,2,3,4...]
            attendance_sheet = create_attendance_sheet(start_week, week_before_semester)

            # get the attendance of the unit
            attendance_list = db.session.query(attendance).filter(attendance.c.unit_code == uid). \
                filter(attendance.c.year == this_year). \
                filter(attendance.c.semester == this_semester).all()

            if attendance_list:

                unit_attendance_percentage_unsorted = calculate_unit_attendance(attendance_list, uid, db, student_unit,
                                                                                this_year, this_semester, start_week)

                unit_attendance_percentage = {k: unit_attendance_percentage_unsorted[k] for k in
                                              sorted(unit_attendance_percentage_unsorted)}

                return render_template('staff_unit_attendance.html', title='Unit Attendance Page',
                                       unit_attendance_percentage=unit_attendance_percentage,
                                       week_list=attendance_sheet[1], uid=uid)

            else:

                # get the week list, e.g. [1,2,3,4...]
                attendance_sheet = create_attendance_sheet(start_week, week_before_semester)

                flash('Please enter a valid unit code.', 'danger')
                return render_template('staff_unit_attendance.html', title='Unit Attendance Page',
                                       unit_attendance_percentage={}, week_list=attendance_sheet[1], uid="")

        else:

            # get the week list, e.g. [1,2,3,4...]
            attendance_sheet = create_attendance_sheet(start_week, week_before_semester)

            flash("Please enter a unit code to view unit attendance, etc: FIT3155_L1", 'info')
            return render_template('staff_unit_attendance.html', title='Unit Attendance Page',
                                   unit_attendance_percentage={}, week_list=attendance_sheet[1], uid="")


@app.route('/late_absent_page', methods=['GET', 'POST'])
@login_required
def late_absent_page():
    if is_staff(current_user):

        if request.method == "POST":
            uid = request.form.get("search_uid").upper()
            uid = ' '.join(uid.split())
            sid = request.form.get("search_sid").upper()
            sid = ' '.join(sid.split())

            if uid and sid:
                attendance_list = db.session.query(attendance).filter(attendance.c.unit_code == uid). \
                    filter(attendance.c.student_id == sid). \
                    filter(attendance.c.year == this_year). \
                    filter(attendance.c.semester == this_semester).all()

                query_student = db.session.query(Student).filter(Student.student_id == sid).first()
                if not query_student:
                    flash("No such student exists.", "danger")
                    return render_template('late_absent_page.html', title='Late Absent Page', late_data=[],
                                           absent_data=[],
                                           student_name="", unit_name="")

                student_name = query_student.last_name + " " + query_student.first_name

                if not attendance_list:

                    check_student_exist_in_unit = db.session.query(student_unit) \
                        .filter(student_unit.c.student_id == sid, student_unit.c.unit_code == uid,
                                student_unit.c.year == this_year, student_unit.c.semester == this_semester).first()

                    if check_student_exist_in_unit:

                        flash("Student has no attendance record.", "warning")
                        return render_template('late_absent_page.html', title='Late Absent Page', late_data=[],
                                               absent_data=[], student_name=student_name, unit_name=uid)
                    else:
                        flash("No information available. Please try again", "warning")
                        return render_template('late_absent_page.html', title='Late Absent Page', late_data=[]
                                               , absent_data=[], student_name="", unit_name="")

                # get the week list, e.g. [1,2,3,4...]
                attendance_sheet = create_attendance_sheet(start_week, week_before_semester)

                late_data = calculate_late_data(attendance_sheet[0], attendance_list)
                absent_data = calculate_absent_data(attendance_sheet[0], attendance_list, start_week)

                return render_template('late_absent_page.html', title='Late Absent Page', late_data=late_data,
                                       absent_data=absent_data, student_name=student_name, unit_name=uid)

            elif not uid and not sid:
                flash("Please enter full information", "danger")
                return render_template('late_absent_page.html', title='Late Absent Page', late_data=[], absent_data=[],
                                       student_name="", unit_name="")
            elif not sid:
                flash("Please enter student id", "danger")
                return render_template('late_absent_page.html', title='Late Absent Page', late_data=[], absent_data=[],
                                       student_name="", unit_name="")
            else:
                flash("Please enter unit code", "danger")
                return render_template('late_absent_page.html', title='Late Absent Page', late_data=[], absent_data=[],
                                       student_name="", unit_name="")

        flash("Please enter student ID and unit code, etc 29036186 and FIT3143_L1", "info")
        return render_template('late_absent_page.html', title='Late Absent Page', late_data=[], absent_data=[],
                               student_name="", unit_name="")


@app.route('/staff_download_attendance/<student_id>', methods=['POST'])
@login_required
def staff_page_download_student_csv(student_id):
    if request.method == 'POST':
        attendance_list = db.session.query(attendance).filter(
            attendance.c.student_id == student_id).all()
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow([('Student ID'), ('Unit'), ('Week'), ('Time In'), ('Time Out'), ('Late'), ('Year'), ('Semester')])
        cw.writerows(attendance_list)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=" + str(student_id) + "_attendance_list.csv"
        output.headers["Content-type"] = "text/csv"
        return output


@app.route('/attendance_data_page', methods=['GET', 'POST'])
@login_required
def attendance_data_page():
    if is_staff(current_user):

        if request.method == "POST":
            sid = request.form.get("search_sid")

            if sid == "":
                flash("Please at least enter a student ID", "danger")
                return render_template('attendance_data_page.html', title='Attendance Data Page', student_name=""
                                       , student_id="", table_data={})

            # get the student details
            student_details = db.session.query(Student).filter(Student.student_id == sid).first()

            if not student_details:
                flash("Please enter a valid student ID", "danger")
                return render_template('attendance_data_page.html', title='Attendance Data Page', student_name=""
                                       , student_id="", table_data={})

            student_id = student_details.student_id
            student_name = student_details.last_name + " " + student_details.first_name

            # get the attendance of the student
            attendance_list = db.session.query(attendance).filter(attendance.c.student_id == sid). \
                filter(attendance.c.year == this_year). \
                filter(attendance.c.semester == this_semester).all()

            table_data = attendance_data_without_sid(attendance_list)

            if not attendance_list:
                flash("This student is not taking any unit. For any assistanec please contact the administration.",
                      "danger")
                return render_template('attendance_data_page.html', title='Attendance Data Page', student_name=""
                                       , student_id="", table_data={})

            else:
                return render_template('attendance_data_page.html', title='Attendance Data Page',
                                       student_name=student_name
                                       , student_id=student_id, table_data=table_data)

        flash("Please enter a student id to view student attendance data list, etc: 29036186", 'info')
        return render_template('attendance_data_page.html', title='Attendance Data Page', student_name=""
                               , student_id="", table_data={})


@app.route('/attendance_analysis_page', methods=['GET', 'POST'])
@login_required
def attendance_analysis_page():
    if is_staff(current_user):

        if request.method == "POST":
            uid = request.form.get("search_uid")

            if uid == "":
                flash("Please at least enter a unit code.", 'danger')
                return render_template('/staff_attendance_analysis.html', title='Attendance Analysis Page', uid=""
                                       , analysis_result={}, class_time_analysis=[], club_clash_analysis=[]
                                       , student_retake_analysis=[], weather_analysis=[], analysis_suggestion="")

            uid = uid.upper()
            uid = ' '.join(uid.split())

            unit_valid = db.session.query(Unit).filter(Unit.unit_code == uid).filter(Unit.unit_offer == True).first()

            if not unit_valid:
                flash("Please enter a valid unit code", "danger")
                return render_template('/staff_attendance_analysis.html', title='Attendance Analysis Page', uid=""
                                       , analysis_result={}, class_time_analysis=[], club_clash_analysis=[]
                                       , student_retake_analysis=[], weather_analysis=[], analysis_suggestion="")

            analysis_result = analysis_algo(uid, db, room_unit, student_unit, student_club, this_year, this_semester,
                                            Weather, Club)
            class_time_analysis = analysis_result['class_start_time_analysis']
            club_clash_analysis = analysis_result['club_clash_analysis']
            student_retake_analysis = analysis_result['student_retake_analysis']
            weather_analysis = analysis_result['weather_analysis']
            analysis_suggestion = analysis_result['analysis_suggestion']

            return render_template('/staff_attendance_analysis.html', title='Attendance Analysis Page', uid=uid,
                                   analysis_result=analysis_result, class_time_analysis=class_time_analysis,
                                   club_clash_analysis=club_clash_analysis,
                                   student_retake_analysis=student_retake_analysis,
                                   weather_analysis=weather_analysis, analysis_suggestion=analysis_suggestion)

        else:
            flash("Please enter a unit code to view unit attendance analytics, etc: FIT3155_L1", 'info')
            return render_template('/staff_attendance_analysis.html', title='Attendance Analysis Page', uid=""
                                   , analysis_result={}, class_time_analysis=[], club_clash_analysis=[]
                                   , student_retake_analysis=[], weather_analysis=[], analysis_suggestion="")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.before_request
def make_session_permanent():
    session.permanent = False


def is_staff(current_user):
    """
    to check if the current user role is student or staff. If it;s staff return True, else log the user out and return
    to the index page
    :param current_user: Flask object, either it's Student or Staff object
    :return: boolean, or render the template to index page
    """

    if current_user.is_authenticated:
        if current_user.email.split("@", 1)[1] == 'student.monash.edu':
            flash("Please login as staff to access this page", "danger")
            logout_user()
            return render_template('/', title='Home')

    return True


@app.errorhandler(Exception)
def handle_error(e):
    try:
        if e.code == 404:
            flash("The page you're looking for was not found", "warning")
            return render_template('index.html', title="Home")
        elif e.code == 401:
            flash("Please login to access this page", "danger")
            return render_template('index.html', title="Home")
        raise e
    except:
        flash("There's a problem with the dashbaord. Please contact the administrator to fix the dashbaord.", 'danger')
        return render_template('index.html', title="Home")
