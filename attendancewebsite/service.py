"""
FILENAME - service.py
CODING - UTF-8
USAGE - all the function that will be used in routes.py. Calculate attendance percentage, extract data, generate
        percentage, attendance analysis and so on. These functions will mainly get inputs passed
        from routes.py which are mainly student_id, unit_code, attendance_list, week_list. It will then return the
        results back to the routes.py to be show in the front-end.
DATE - Started Aug 9 2020
NOTES - Python version used is 3.7 and the database adapter used to connect with PostgreSQl is the psycopg binary
CODED BY - LIM JIN YUNG
"""

# Python Library
from datetime import datetime, timedelta, time
import random

week_length = 13

analysis_priority = {
    'class_start_time_analysis': 1,
    'club_clash_analysis': 2,
    'student_retake_analysis': 3,
    'weather_analysis': 4
}


def find_this_week(start_week):
    """
    calculation for this week by using the current date subtract the start date of the semester and divide by 7
    :return: type integer indicates the current week
    """

    # calculation for this week
    strt_date = datetime.date(start_week)
    current_date = datetime.date(datetime.now())

    # calculation for this week
    num_of_days = abs(current_date - strt_date).days
    this_week = (num_of_days // 7) + 1

    return this_week


def get_unit(attendance_list):
    """
    Take the attendance list and extract all the units using a for loop
    :param attendance_list: a list of attendance list,
    e.g. [('29036186', 'FIT3081_L1', 1, datetime.datetime(2020, 8, 3, 10, 10),
    datetime.datetime(2020, 8, 3, 12, 0), False, '2020', '2'), ('29036186', 'FIT3081_L1', 2,
    datetime.datetime(2020, 8, 10, 10, 2), datetime.datetime(2020, 8, 10, 12, 1), False, '2020', '2')]
    :return: a list of units only, e.g. ['FIT3155_L1', 'FIT3155_T4', 'FIT3081_L1', 'FIT3081_T1', 'FIT2102_L1',
    'FIT2102_T1', 'FIT3143_L1', 'FIT3143_T1']
    """
    units = []

    for i in range(len(attendance_list)):
        if attendance_list[i][1] not in units:
            units.append(attendance_list[i][1])

    return units


def create_attendance_sheet(start_week, week_before_semester):
    """
    Create two list of week list based on the start_week query from the database and this week. The attendance sheet
    length will be depending on this week.
    :return: two list of weeks list. e.g. ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10'])
    """
    week_list = []

    this_week = find_this_week(start_week)

    for i in range(week_length):
        week_list.append(start_week + timedelta(days=(7 * i)))

    # exclude the week of semester break
    if week_before_semester < this_week:
        this_week -= 1
        week_list.remove(week_list[week_before_semester])

    # create two types of week list, one is for calculation, another is for display on chart
    # check_attendance_sheet is for calculation
    # chart_week_display is for display on chart
    check_attendance_sheet = []
    for k in range(len(week_list[0:this_week])):
        check_attendance_sheet.append(k + 1)

    chart_week_display = []
    for l in range(len(check_attendance_sheet)):
        chart_week_display.append("W" + str(check_attendance_sheet[l]))

    # ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10'])
    return check_attendance_sheet, chart_week_display


def generate_attendance_percentage(attendance_sheet, student_attendance_week_list):
    """
    Generate logged in student every week unit's attendance percentage by
    dividing student's every unit week list with attendance sheet week list
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

            count_percentage = round(((len(mark_attendance) / len(attendance_sheet[0:i])) * 100), 2)

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
    Sort the unit for front-end purposes in chart
    :param units: a list of units, e.g. ['FIT3155_L1', 'FIT3081_L1', 'FIT3081_T1', 'FIT3155_T1']
    :param attendance_list: a list of attendance list,
    e.g. [('29036186', 'FIT3081_L1', 1, datetime.datetime(2020, 8, 3, 10, 10),
    datetime.datetime(2020, 8, 3, 12, 0), False, '2020', '2'), ('29036186', 'FIT3081_L1', 2,
    datetime.datetime(2020, 8, 10, 10, 2), datetime.datetime(2020, 8, 10, 12, 1), False, '2020', '2')]
    :return: attendance_list sorted by units
    """
    student_attendance = {}

    for i in range(len(units)):
        student_attendance[units[i]] = []

    for j in range(len(attendance_list)):
        unit_in_attendance_list = attendance_list[j][1]
        student_attendance[unit_in_attendance_list].append(attendance_list[j][2])

        student_attendance[attendance_list[j][1]].sort()

    return student_attendance


def extract_units(attendance_list, selected_units):
    """
    Pop out the unit's attendance data that's not in inside selected_units list
    :param attendance_list: a list of attendance data, e.g.
    [('29036186', 'FIT3081_L1', 3, datetime.datetime(2020, 8, 17, 10, 15), datetime.datetime(2020, 8, 17, 12, 7), False,
    '2020', '2'),...,...]
    :param selected_units: a list of units, e.g. ['FIT3155_L1', 'FIT3081_L1', 'FIT3155_T1']
    :return: attendance_list with extracted the units given by selected units list
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
    """
    calculate the unit
    :param attendance_sheet: a list of attendance week list, e.g. [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    :param student_attendance_week_list: a dictionary type of student's attendance list,
    e.g. {'FIT3081_L2': [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12], 'FIT3081_T1': [1, 3, 4, 5, 6, 7, 9, 10, 11, 12],
    'FIT2102_L1': [2, 3, 4, 5, 6, 7, 9, 10, 11, 12],...}
    :return: a dict of unit and it's total percentage, e.g. {'FIT3081_L2': 100.0, 'FIT3081_T1': 90.9090909090909,
    'FIT2102_L1': 90.9090909090909}
    """
    student_attendance_percentage = {}

    # for every unit's week list in the dict, take length of the list  and
    # divide with the attendance week list to obtain the total percentage of every unit
    for key in student_attendance_week_list:
        student_attendance_percentage[key] = round(((len(student_attendance_week_list[key]) /
                                                     len(attendance_sheet)) * 100), 2)

    return student_attendance_percentage


def calculate_unit_attendance(attendance_list, unit_code, db, student_unit, this_year, this_semester, start_week):
    """
    Calculate the unit weekly attendance by comparing weekly student's attendance list with attendance sheet
    :param attendance_list: a list of attendance list,
           e.g. [('29036186', 'FIT3081_L1', 1, datetime.datetime(2020, 8, 3, 10, 10),
           datetime.datetime(2020, 8, 3, 12, 0), False, '2020', '2'), ('29036186', 'FIT3081_L1', 2,
           datetime.datetime(2020, 8, 10, 10, 2), datetime.datetime(2020, 8, 10, 12, 1), False, '2020', '2')]
    :param unit_code: a string of unit code. The unit code to be calculate the weekly percentage
    :param db: the database engine to query student_unit
    :param student_unit: the student_unit model from model.py
    :param this_year: current year query from database passed in from routes.py
    :param this_semester: current semester query from database passed in from routes.py
    :param start_week: the first week of semester query from database passed in from routes.py
    :return: unit weekly attendance in a dict format, e.g. {1: 88.24, 2: 88.24, 3: 79.41, 4: 94.12,
             5: 97.06, 6: 88.24, 7: 88.24, 8: 79.41, 9: 88.24, 10: 94.12, 11: 88.24}
    """
    # get all the students that are taking the unit
    # e.g. [('29036186', 'FIT3155_L1', '2020', '2'), ('29821894', 'FIT3155_L1', '2020', '2'), ...]
    student_list = db.session.query(student_unit).filter(student_unit.c.unit_code == unit_code).filter(
        student_unit.c.year == this_year).filter(student_unit.c.semester == this_semester).all()

    # total number of student in the unit
    total_attendance_number = len(student_list)

    # unit attendance dict will hold the weekly attendance data
    unit_attendance = {}

    # find_this_week function will return this week
    this_week = find_this_week(start_week)

    # initialize the unit_attendance dict from week 1 until this week
    for all_week in range(1, this_week):
        unit_attendance[all_week] = 0

    # check if the the week appears, if yes increment week_count
    for i in range(len(attendance_list)):

        week_count = attendance_list[i][2]
        if week_count in unit_attendance:
            unit_attendance[week_count] += 1
        else:
            unit_attendance[week_count] = 1

    # calculate the percentage by dividing the total number of students in class
    for week in unit_attendance:
        unit_attendance[week] = round(((unit_attendance[week] / total_attendance_number) * 100), 2)

    return unit_attendance


def attendance_data_without_sid(attendance_list):
    """
    Take in a dict of attendance list and take off the student id to present the table on staff attendance table page
    :param attendance_list: a list of attendance list,
    e.g. {('29036186', 'FIT3081_L1', 1, datetime.datetime(2020, 8, 3, 10, 10),
    datetime.datetime(2020, 8, 3, 12, 0), False, '2020', '2'), ('29036186', 'FIT3081_L1', 2,
    datetime.datetime(2020, 8, 10, 10, 2), datetime.datetime(2020, 8, 10, 12, 1), False, '2020', '2')}
    :return: a list of attendance list without student id
    """
    table_data = []

    for i in range(len(attendance_list)):
        table_col = []
        for j in range(1, len(attendance_list[i])):
            table_col.append(attendance_list[i][j])
        table_data.append(table_col)

    return table_data


def calculate_late_data(week_list, attendance_list):
    """
    Calculate a student's late attendance percentage by comparing with week list and return the percentage with late
    attendance list to display on the late/absent page
    :param week_list: week list from week 1 until this week, e.g. [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    :param attendance_list: a list of attendance list,
    e.g. [('29036186', 'FIT3081_L1', 1, datetime.datetime(2020, 8, 3, 10, 10),
    datetime.datetime(2020, 8, 3, 12, 0), False, '2020', '2'), ('29036186', 'FIT3081_L1', 2,
    datetime.datetime(2020, 8, 10, 10, 2), datetime.datetime(2020, 8, 10, 12, 1), False, '2020', '2')]
    :return: a float type of late_percentage and a list of late attendance consist of the late attendance data
    """

    late_attendance = []

    # get the late attendance list by check is the column 'late' in attendance list is True
    # append the data into the late attendance list if True
    for check_attendance in attendance_list:
        late_bool = check_attendance[5]
        if late_bool:
            late_attendance.append([check_attendance[2], check_attendance[3].strftime("%m/%d/%Y, %H:%M:%S")
                                       , check_attendance[4].strftime("%m/%d/%Y, %H:%M:%S")])

    # calculate the late percentage by dividing the length of late attendance list with the length of week list
    late_percentage = round((len(late_attendance) / len(week_list)) * 100, 2)

    return late_percentage, late_attendance


def calculate_absent_data(week_list, attendance_list, start_week):
    """
    Calculate a student's absent attendance percentage by comparing student's present weeks with the week list
    :param week_list: week list from week 1 until this week, e.g. [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    :param attendance_list: a list of attendance list,
    e.g. [('29036186', 'FIT3081_L1', 1, datetime.datetime(2020, 8, 3, 10, 10),
    datetime.datetime(2020, 8, 3, 12, 0), False, '2020', '2'), ('29036186', 'FIT3081_L1', 2,
    datetime.datetime(2020, 8, 10, 10, 2), datetime.datetime(2020, 8, 10, 12, 1), False, '2020', '2')]
    :param start_week: the first week of semester query from database passed in from routes.py
    :return: a float type of absent_percentage
    """

    absent_attendance = []
    present_week = []
    absent_week = []

    # check from attendance list which week the student is present in class and append into the attendance list
    for attendance_week in attendance_list:
        week_value = attendance_week[2]
        present_week.append(week_value)

    # check from attendance list which week the student is absent in class and append into the attendance list
    for check_week in week_list:
        if check_week not in present_week:
            absent_week.append(check_week)

    for each_absent_week in absent_week:
        absent_datetime = start_week + timedelta(days=(each_absent_week - 1))
        absent_attendance.append([each_absent_week, absent_datetime.strftime("%d/%m/%Y")])

    # calculate the total percentage of the absent attendance
    absent_percentage = round(((len(absent_week)) / len(week_list)) * 100, 2)

    return absent_percentage, absent_attendance


##########################################################
### Attendance Analysis Algorithm
##########################################################


def get_class_start_time(unit_code, db, room_unit, Club):
    """
    Check from database if the class time of the class is too early or too late
    :param unit_code: a string of unit code
    :param db: the database engine to query room_unit, Club
    :param room_unit: the room_unit model from models.py passed in from routes.py
    :param Club: the Club model from models.py passed in from routes.py
    :return: tuple containing first boolean, and second a list of possible class start time. This list can be empty
    """

    # query the unit's class time
    result_set = db.session.query(room_unit).filter(room_unit.c.unit_code == unit_code).all()

    class_start_time = result_set[0][2]

    # if the class start time is between 8am to 10 am
    # if yes, return True and a list of possible class start time
    if (class_start_time >= time(8, 0, 0)) and (class_start_time <= time(10, 0, 0)):
        return True, get_possible_class_start_time(unit_code, db, room_unit, Club)

    # if the class start time is more than 6pm
    # if yes, return True and a list of possible class start time
    elif class_start_time >= time(18, 0, 0):
        return True, get_possible_class_start_time(unit_code, db, room_unit, Club)

    # return False and an empty list if both is false
    else:
        return False, []


def get_possible_class_start_time(unit_code, db, room_unit, Club):
    """
    This function is to get all the possible class start time when the class start time of the unit code passed in as an argument is too
    early or too late.
    How we consider a possible class start time is clashing with a club if it fulfills the following condition
    |(Club 1)--------------------------|(Class Start Time)--------------------------------------|(Club 2)
    The Class Start Time will not clash with the frist club if the Class Starts after the first club has ended
    The Class Start Time will not clash with the second club if the class ends before the second club starts
    :param unit_code: the unit code where the class start time is too early or too late
    :param db: the database ORM object to access the database to do queries
    :param room_unit: the room_unit table in the database
    :param Club: the Club table in the database.
    """
    result_set = db.session.query(room_unit).filter(room_unit.c.unit_code == unit_code).all()

    class_day = result_set[0][4]
    class_duration = result_set[0][3]

    result_set = db.session.query(room_unit).filter(room_unit.c.day == class_day).all()

    classes_end_time = {}

    for c in result_set:
        c_start_time = timedelta(hours=c[2].hour, minutes=c[2].minute, seconds=c[2].second)
        c_duration = timedelta(hours=0, minutes=0, seconds=c[3])
        c_end_time = c_start_time + c_duration

        if (c_end_time >= timedelta(hours=10, minutes=0, seconds=0)) and (c_end_time < timedelta(hours=18, minutes=0,
                                                                                                 seconds=0)):
            classes_end_time[str(c_end_time)] = c_end_time

    possible_class_start_time = []

    result_set = db.session.query(Club).all()

    for key in classes_end_time.keys():
        crash = False
        class_start_time = classes_end_time[key]

        for club in result_set:
            if club.day == class_day:
                club_start_time = timedelta(hours=club.club_start_time.hour, minutes=club.club_start_time.minute,
                                            seconds=club.club_start_time.second)
                time_diff = (class_start_time - club_start_time).total_seconds()

                if (time_diff > -class_duration) and (time_diff <= club.club_duration):
                    crash = True
                    break

        if not crash:
            possible_class_start_time.append(key)

    possible_class_start_time.sort()

    return possible_class_start_time


def get_clubs_datetime(unit_code, db, room_unit, Club):
    """
    Check if the unit's class time is clash with any clubs by comparing the class time with every clubs' start time. If
    there's a clash it'll find the time difference between the class and the club
    :param unit_code: a string type of unit code
    :return:
    """

    # get the class time of the unit
    result_set = db.session.query(room_unit).filter(room_unit.c.unit_code == unit_code).all()

    class_duration = result_set[0][3]
    class_day = result_set[0][4]
    class_start_time = timedelta(hours=result_set[0][2].hour, minutes=result_set[0][2].minute,
                                 seconds=result_set[0][2].second)

    # from database query all Club's information
    result_set = db.session.query(Club).all()

    # clubs is to hold any Clubs' club code, club name and a list of possible class time
    # that clashes with the class. The list can be empty if there're no clashes
    clubs = []
    for club in result_set:

        club_start_time = timedelta(hours=club.club_start_time.hour, minutes=club.club_start_time.minute,
                                    seconds=club.club_start_time.second)

        if club.day == class_day:
            # calculate the time difference between the class and the club, it can be positive/negative indicates the
            # if the time difference is negative, class starts earlier then the club
            # else if the time difference is positive, class start later then the club
            time_diff = (class_start_time - club_start_time).total_seconds()

            if (time_diff > -class_duration) and (time_diff < club.club_duration):
                clubs.append([club.club_name, club.club_code, time_diff])

    return clubs


def retake_num_of_students(unit_code, year, sem, db, student_unit):
    """
    query students from database and check if there's any student has data in previous semester is also appearing in
    current semester. Record the numbers of students and return it in a list
    :param unit_code: a string type of unit code
    :param year: a string type of year, semester year
    :param sem: a string type of semester, current semester
    :return: an integer type num_of_studens indicates the number of student retake the unit
    """
    result_set = db.session.query(student_unit.c.student_id, student_unit.c.year, student_unit.c.semester) \
        .filter(student_unit.c.unit_code == unit_code).order_by(student_unit.c.student_id.asc()).all()

    start = 0
    stop = len(result_set)

    num_of_students = 0

    while start < stop - 1:
        student_id = result_set[start][0]
        student_id_nxt = result_set[start + 1][0]

        if student_id == student_id_nxt:
            duplicates = [result_set[start], result_set[start + 1]]

            i = start + 2

            while i < stop:
                student_id_nxt = result_set[i][0]

                if student_id != student_id_nxt:
                    break

                duplicates.append(result_set[i])
                i += 1

            for k in range(len(duplicates)):

                if (duplicates[k][1] == year) and (duplicates[k][2] == sem):
                    num_of_students += 1
                    break

            start = i

        else:
            start += 1

    return num_of_students


def analysis_algo(unit_code, db, room_unit, student_unit, student_club, this_year, this_semester, Weather, Club):
    """
    the main function to run the unit analysis where a dict analysis_list will hold all the analysis result.
    This function consist 5 parts:
    Part 1: check the class time by calling the function get_class_start_time
    Part 2: check the if there's any club clashes with the class. If the numbers in the clubs are more than 1/4
            , it'll return True and run the function get_possible_class_time to suggest another class time to the staff
    Part 3: check if there's more than half of the students in the class retake the unit. If yes, return True and the
            number of students retake, else if it's not more than half, return False and the number of students retake
    Part 4: check the weather table if the weather condition for 'Rain' and 'Thunderstorm' is more than half, if it's
            more than half, return True and the weather data, else return False
    Part 5: based on the attendance_list, sort the factors by their priority and give the suggestions accordingly.
    :param unit_code: a string type of unit code
    :return: a list of strings indicates the suggestions based on the analysis
    """

    analysis_list = {}
    analysis_suggestion = []

    # (1) checking class time
    flag, possible_class_start_time = get_class_start_time(unit_code, db, room_unit, Club)
    analysis_list['class_start_time_analysis'] = flag, possible_class_start_time

    # (2) checking club and class clash
    clubs = get_clubs_datetime(unit_code, db, room_unit, Club)
    if len(clubs) > 0:

        students_in_club_list = []
        students_in_class_list = []
        student_in_clashed_club = 0

        # get students in clashed club(s)
        for club in clubs:
            get_students_in_club = db.session.query(student_club).filter(student_club.c.club_code == club[1]).all()
            for students_in_club in get_students_in_club:
                students_in_club_list.append(students_in_club[0])

        # get students in class
        get_students_in_class = db.session.query(student_unit).filter(student_unit.c.unit_code == unit_code) \
            .filter(student_unit.c.year == this_year).filter(student_unit.c.semester == this_semester).all()
        for students_in_class in get_students_in_class:
            students_in_class_list.append(students_in_class[0])

        # check how much student is in clashed club(s)
        for check_every_student in students_in_class_list:
            if check_every_student in students_in_club_list:
                student_in_clashed_club += 1

        # check how many student(s) in clashed club(s)
        if student_in_clashed_club > (len(get_students_in_class) / 4):
            club_other_class_time = get_possible_class_start_time(unit_code, db, room_unit, Club)
            analysis_list['club_clash_analysis'] = True, club_other_class_time, clubs
        else:
            analysis_list['club_clash_analysis'] = False, [], clubs
    else:
        analysis_list['club_clash_analysis'] = False, [], clubs

    # (3) checking numbers of retake student in a class
    num_of_retake_students = retake_num_of_students(unit_code, this_year[0], this_semester[0], db, student_unit)
    if num_of_retake_students > 0:
        total_number_student_unit = db.session.query(student_unit).filter(student_unit.c.unit_code == unit_code) \
            .filter(student_unit.c.year == this_year).filter(student_unit.c.semester == this_semester).all()
        if num_of_retake_students > (len(total_number_student_unit) / 2):
            analysis_list['student_retake_analysis'] = True, num_of_retake_students, round(
                (num_of_retake_students / len(total_number_student_unit) * 100), 2)
        else:
            analysis_list['student_retake_analysis'] = False, num_of_retake_students, round(
                (num_of_retake_students / len(total_number_student_unit) * 100), 2)
    else:
        analysis_list['student_retake_analysis'] = False, 0, 0

    # (4) check how weather affect the class
    unit_weather_list = db.session.query(Weather).filter(Weather.unit_code == unit_code) \
        .filter(Weather.year == this_year).filter(Weather.semester == this_semester).all()

    count_bad_weather = 0
    bad_weather_standard = ['Thunderstorm', 'Rain']
    for everyday_weather in unit_weather_list:
        if everyday_weather.weather in bad_weather_standard:
            count_bad_weather += 1

    if count_bad_weather > (len(unit_weather_list) / 2):
        analysis_list['weather_analysis'] = True, round((count_bad_weather / len(unit_weather_list) * 100),
                                                        2), unit_weather_list
    else:
        analysis_list['weather_analysis'] = False, round((count_bad_weather / len(unit_weather_list) * 100),
                                                         2), unit_weather_list

    # (5) giving suggestion
    for key in analysis_list.keys():
        if analysis_list[key][0]:
            analysis_suggestion.append(analysis_priority[key])

    suggestion = ""

    if analysis_suggestion:
        analysis_suggestion.sort()
        case = 0
        while case < len(analysis_suggestion):

            if analysis_suggestion[case] == 1:
                suggestion += "Please choose another class time if there's any other time slots available"
                break

            if analysis_suggestion[case] == 2:
                suggestion += ("Class time clashed with club(s). "
                               "Please choose another time slot to avoid low attendance rate if available.")
                break

            if analysis_suggestion[case] == 3:
                suggestion += ("There're quite a lot of student retake this unit. "
                               "Consider to add some other new material into teaching syllabus?")
                break

            if analysis_suggestion[case] == 4:
                suggestion += ("It's always bad weather when your class starts. "
                               "We're sorry but we don't have the ability to control weather right now.")
                break
    else:
        suggestion += "Class is good!"

    analysis_list['analysis_suggestion'] = suggestion

    return analysis_list


all_units = ['FIT2004_T1', 'FIT2004_T2', 'FIT2004_T3', 'FIT2004_T4', 'FIT3155_L1', 'FIT3155_L2', 'FIT3161_T1',
             'FIT3162_T1', 'FIT2102_L1', 'FIT2102_L2', 'FIT3143_T4', 'FIT3143_T3', 'FIT3143_T2', 'FIT3143_T1',
             'FIT3162_L1', 'FIT3081_L2', 'FIT3081_L1', 'FIT3155_T1', 'FIT3155_T2', 'FIT3155_T3', 'FIT3155_T4',
             'FIT3161_L1', 'FIT2004_L1', 'FIT2004_L2', 'FIT2102_T1', 'FIT2102_T3', 'FIT2102_T2', 'FIT3081_T2',
             'FIT3143_L2', 'FIT3143_L1', 'FIT3081_T1']

# for unit in all_units:
#     print(unit, analysis_algo(unit, db, room_unit, student_unit, student_club, this_year, this_semester, Weather, Club))
