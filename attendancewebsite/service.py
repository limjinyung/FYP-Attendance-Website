from attendancewebsite import db
from attendancewebsite.models import Semester, student_unit
from datetime import datetime, timedelta

start_week = db.session.query(Semester.start_date).order_by(Semester.start_date.desc()).first()
this_year = db.session.query(Semester.year).order_by(Semester.start_date.desc()).first()
this_semester = db.session.query(Semester.semester).order_by(Semester.start_date.desc()).first()
start_week = datetime.strptime(start_week[0], '%Y-%m-%d').date()
week_length = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


def get_unit(attendance_list):
    units = []

    for i in range(len(attendance_list)):
        if attendance_list[i][1] not in units:
            units.append(attendance_list[i][1])

    return units


def create_attendance_sheet():
    """
    Create two list of week list based on the start_week query from the database, the list of week will be 12 weeks long
    :return: two list of weeks list. e.g. ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10'])
    """
    week_list = []

    for i in range(12):
        week_list.append(start_week + timedelta(days=(7 * i)))

    this_week = 0
    today_str = datetime.today().strftime('%Y-%m-%d')
    today = datetime.strptime(today_str, '%Y-%m-%d').date()

    # initially the week is 12 weeks long,
    # use for loop to get the current week
    for j in range(len(week_list)):
        if j == 0:
            if (today == week_list[j]) or (today < week_list[j + 1]):
                this_week = j + 1
                break
        else:
            if (today == week_list[j]) or (week_list[j - 1] < today < week_list[j + 1]):
                this_week = j + 1
                break

    # create two types of week list, one is for calculation, another is for display on chart
    check_attendance_sheet = []
    for k in range(len(week_list[0:this_week])):
        check_attendance_sheet.append(k + 1)

    chart_week_display = []
    for l in range(len(check_attendance_sheet)):
        chart_week_display.append("W" + str(check_attendance_sheet[l]))

    return check_attendance_sheet, chart_week_display


def generate_attendance_percentage(attendance_sheet, student_attendance_week_list):
    """
    Generate logged in student unit's attendance list
    :param attendance_sheet: week list, e.g. [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    :param student_attendance_week_list: a dictionary of unit and unit's attendance present week,
    e.g. {'FIT3155_L1': [2, 4, 6], 'FIT3081_L1': [1, 2, 3, 4, 5], 'FIT3081_T1': [1, 2, 3, 4], 'FIT3155_T1': [1, 3, 4]}
    :return: a dictionary of units and unit's attendance data
    e.g. {'FIT3155_L1': [0.0, 50.0, 33.3333], 'FIT3081_L1': [100.0, 100.0, 100.0, 100.0]}
    """
    student_attendance_percentage = {}

    for key in student_attendance_week_list:

        mark_attendance = []
        mark_attendance_percentage = []

        for i in range(1, len(attendance_sheet) + 1):

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
    """
    Sort the unit for front-end purposes
    :param units: a list of units, e.g. ['FIT3155_L1', 'FIT3081_L1', 'FIT3081_T1', 'FIT3155_T1']
    :param attendance_list: a list of attendance list,
    e.g. [('29036186', 'FIT3081_L1', 1, datetime.datetime(2020, 8, 3, 10, 10),
    datetime.datetime(2020, 8, 3, 12, 0), False, '2020', '2'), ('29036186', 'FIT3081_L1', 2, datetime.datetime(2020, 8, 10, 10, 2), datetime.datetime(2020, 8, 10, 12, 1), False, '2020', '2')]
    :return:
    """
    student_attendance = {}

    for i in range(len(units)):
        student_attendance[units[i]] = []

    for j in range(len(attendance_list)):
        if attendance_list[j][1] in student_attendance:
            student_attendance[attendance_list[j][1]].append(attendance_list[j][2])

        student_attendance[attendance_list[j][1]].sort()

    return student_attendance


def extract_units(attendance_list, selected_units):
    """
    Pop out the unit's attendance data that's not in inside selected_units list
    :param attendance_list: a list of attendance data, e.g.
    [('29036186', 'FIT3081_L1', 3, datetime.datetime(2020, 8, 17, 10, 15), datetime.datetime(2020, 8, 17, 12, 7), False,
    '2020', '2'),...,...]
    :param selected_units: a list of units, e.g. ['FIT3155_L1', 'FIT3081_L1', 'FIT3155_T1']
    :return:
    """
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


def extract_student_id(attendance_list):

    table_data = []

    for i in range(len(attendance_list)):
        table_col = []
        for j in range(1, len(attendance_list[i])):
            table_col.append(attendance_list[i][j])
        table_data.append(table_col)

    return table_data