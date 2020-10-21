from attendancewebsite import db
from attendancewebsite.models import Semester, student_unit, attendance, room_unit, Club, Weather, student_club
from datetime import datetime, timedelta, time
from sqlalchemy.sql import func, and_
import random

start_week = db.session.query(Semester.start_date).order_by(Semester.start_date.desc()).first()
this_year = db.session.query(Semester.year).order_by(Semester.start_date.desc()).first()
this_semester = db.session.query(Semester.semester).order_by(Semester.start_date.desc()).first()
semester_break = db.session.query(Semester.week_before_sembreak).order_by(Semester.start_date.desc()).first()
start_week = datetime.strptime(start_week[0], '%Y-%m-%d')
# start_week = "2020-08-03"
# this_year = "2020"
# this_semester = "2"
week_length = 13
analysis_priority = {
    'class_start_time_analysis': 1,
    'club_clash_analysis': 2,
    'student_retake_analysis': 3,
    'weather_analysis': 4
}


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

    for i in range(week_length):
        week_list.append(start_week + timedelta(days=(7 * i)))

    strt_date = datetime.date(start_week)
    current_date = datetime.date(datetime.now())
    week_before_semester = semester_break[0]

    num_of_days = abs(current_date - strt_date).days
    this_week = (num_of_days // 7) + 1

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
        unit_attendance[week] = (unit_attendance[week] / total_attendance_number) * 100

    return unit_attendance


def extract_student_id(attendance_list):
    table_data = []

    for i in range(len(attendance_list)):
        table_col = []
        for j in range(1, len(attendance_list[i])):
            table_col.append(attendance_list[i][j])
        table_data.append(table_col)

    return table_data


def calculate_late_data(week_list, attendance_list):
    late_attendance = []

    for check_attendance in attendance_list:
        late_bool = check_attendance[6]
        if late_bool:
            late_attendance.append([check_attendance[2], check_attendance[3].strftime("%m/%d/%Y, %H:%M:%S")
                                       , check_attendance[4].strftime("%m/%d/%Y, %H:%M:%S")])

    # calculate the late percentage
    late_percentage = round((len(late_attendance) / len(week_list)) * 100, 2)

    return late_percentage, late_attendance


def calculate_absent_data(week_list, attendance_list):
    # TODO: return a list of absent data
    absent_attendance = []
    present_week = []
    absent_week = []

    for attendance_week in attendance_list:
        week_value = attendance_week[2]
        present_week.append(week_value)

    for check_week in week_list:
        if check_week not in present_week:
            absent_week.append(check_week)

    absent_percentage = round(((len(absent_week)) / len(week_list)) * 100, 2)

    return absent_percentage


##########################################################
### Attendance Analysis Algorithm
##########################################################


def get_class_start_time(unit_code):
    result_set = db.session.query(room_unit).filter(room_unit.c.unit_code == unit_code).all()

    class_start_time = result_set[0][2]

    if (class_start_time >= time(8, 0, 0)) and (class_start_time <= time(10, 0, 0)):
        return True, get_possible_class_start_time(unit_code)

    elif class_start_time >= time(18, 0, 0):
        return True, get_possible_class_start_time(unit_code)

    else:
        return False, []


def get_possible_class_start_time(unit_code):
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

    return possible_class_start_time


def get_clubs_datetime(unit_code):
    result_set = db.session.query(room_unit).filter(room_unit.c.unit_code == unit_code).all()

    class_duration = result_set[0][3]
    class_day = result_set[0][4]
    class_start_time = timedelta(hours=result_set[0][2].hour, minutes=result_set[0][2].minute,
                                 seconds=result_set[0][2].second)

    result_set = db.session.query(Club).all()

    clubs = []
    for club in result_set:

        club_start_time = timedelta(hours=club.club_start_time.hour, minutes=club.club_start_time.minute,
                                    seconds=club.club_start_time.second)

        if club.day == class_day:
            time_diff = (class_start_time - club_start_time).total_seconds()

            if (time_diff > -class_duration) and (time_diff <= club.club_duration):
                clubs.append([club.club_name, club.club_code, time_diff])

    return clubs


def get_study_year(unit_code):
    return unit_code[3]


def retake_num_of_students(unit_code, year, sem):
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


# current week -> into the "week" argument
def get_current_weather(unit_code, week):
    result_set = db.session.query(Weather.weather).filter(Weather.unit_code == unit_code, Weather.week == week).all()

    status = result_set[0].weather

    return status


def analysis_algo(unit_code):

    analysis_list = {}
    analysis_suggestion = []

    # (1) checking class time
    flag, possible_class_start_time = get_class_start_time(unit_code)
    analysis_list['class_start_time_analysis'] = flag, possible_class_start_time

    # (2) checking club and class clash
    clubs = get_clubs_datetime(unit_code)
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
        get_students_in_class = db.session.query(student_unit).filter(student_unit.c.unit_code == unit_code)\
            .filter(student_unit.c.year == this_year).filter(student_unit.c.semester == this_semester).all()
        for students_in_class in get_students_in_class:
            students_in_class_list.append(students_in_class[0])

        # check how much student is in clashed club(s)
        for check_every_student in students_in_class_list:
            if check_every_student in students_in_club_list:
                student_in_clashed_club += 1

        # check how many student(s) in clashed club(s)
        if student_in_clashed_club > (len(get_students_in_class)/4):
            club_other_class_time = get_possible_class_start_time(unit_code)
            analysis_list['club_clash_analysis'] = True, club_other_class_time, clubs
        else:
            analysis_list['club_clash_analysis'] = False, [], clubs
    else:
        analysis_list['club_clash_analysis'] = False, [], clubs

    # (3) checking numbers of retake student in a class
    num_of_retake_students = retake_num_of_students(unit_code, this_year[0], this_semester[0])
    if num_of_retake_students > 0:
        total_number_student_unit = db.session.query(student_unit).filter(student_unit.c.unit_code == unit_code)\
            .filter(student_unit.c.year == this_year).filter(student_unit.c.semester == this_semester).all()
        if num_of_retake_students > (len(total_number_student_unit)/2):
            analysis_list['student_retake_analysis'] = True, num_of_retake_students, round((num_of_retake_students/len(total_number_student_unit)*100), 2)
        else:
            analysis_list['student_retake_analysis'] = False, num_of_retake_students, round((num_of_retake_students/len(total_number_student_unit)*100), 2)
    else:
        analysis_list['student_retake_analysis'] = False, 0, 0

    # (4) check how weather affect the class
    unit_weather_list = db.session.query(Weather).filter(Weather.unit_code == unit_code)\
        .filter(Weather.year == this_year).filter(Weather.semester == this_semester).all()

    count_bad_weather = 0
    bad_weather_standard = ['Thunderstorm', 'Rain']
    for everyday_weather in unit_weather_list:
        if everyday_weather.weather in bad_weather_standard:
            count_bad_weather += 1

    if count_bad_weather > (len(unit_weather_list)/2):
        analysis_list['weather_analysis'] = True, round((count_bad_weather/len(unit_weather_list)*100),2), unit_weather_list
    else:
        analysis_list['weather_analysis'] = False, round((count_bad_weather/len(unit_weather_list)*100),2), unit_weather_list

    # (5) giving suggestion
    for key in analysis_list.keys():
        if analysis_list[key][0]:
            analysis_suggestion.append(analysis_priority[key])

    if analysis_suggestion:
        analysis_suggestion.sort()
        case = 0
        suggestion = []
        connector = ['Other than that, ', 'Besides that, ', 'Aside from that, ', 'Also, ']
        final_suggestion = ""
        while case < len(analysis_suggestion):

            if analysis_suggestion[case] == 1 and analysis_list['class_start_time_analysis'][1] != []:
                suggestion.append("Please choose another class time as there're some other time slot for the class.")
                break
            elif analysis_suggestion[case] == 1 and analysis_list['class_start_time_analysis'][1] == []:
                suggestion.append("Class time is too early/late but there's no other time slots available.")
                case += 1

            if analysis_suggestion[case] == 2 and analysis_list['club_clash_analysis'][2] != []:
                suggestion.append("Class time clashed with club(s). "
                                  "Please choose another time slot to avoid low attendance rate.")
                break
            elif analysis_suggestion[case] == 2 and analysis_list['club_clash_analysis'][2] == []:
                suggestion.append("Class time clashed with club(s) but there's aren't any more time slots left.")
                case += 1

            if analysis_suggestion[case] == 3:
                suggestion.append("There're quite a lot of retake student in your unit. "
                                  "Consider to add some other new material into teaching syallbus?")
                break

            if analysis_suggestion[case] == 4:
                suggestion.append("It's always bad weather when your class starts. "
                                  "We're sorry but we don't have the ability to control weather right now.")
                break

        if len(suggestion) == 1:
            final_suggestion = suggestion[0]
        else:
            for suggestion_index in range(len(suggestion)):
                if suggestion_index == 0:
                    final_suggestion += suggestion[suggestion_index]
                else:
                    final_suggestion += random.choice(connector)
                    final_suggestion += suggestion[suggestion_index].lower()
    else:
        final_suggestion = "Class is good!"

    analysis_list['analysis_suggestion'] = final_suggestion

    return analysis_list


def simple_algo(unit_code):
    flag, possible_class_start_time = get_class_start_time(unit_code)
    if flag and len(possible_class_start_time) > 0:
        return 1, possible_class_start_time  # it may be an empty list

    else:
        clubs = get_clubs_datetime(unit_code)
        if len(clubs) > 0:
            club_other_class_time = get_possible_class_start_time(unit_code)
            return 2, clubs, club_other_class_time
            # list of list and each inner list -> club name, time diff
            # negative, class starts earlier than the club
            # positive, class starts later than the class

        else:
            num_of_students = retake_num_of_students(unit_code, this_year[0], this_semester[0])
            if num_of_students > 0:
                return 3, num_of_students  # integer

            else:
                return 4, get_study_year(unit_code)  # string


all_units = ['FIT2004_T1', 'FIT2004_T2', 'FIT2004_T3', 'FIT2004_T4', 'FIT3155_L1', 'FIT3155_L2', 'FIT3161_T1',
             'FIT3162_T1', 'FIT2102_L1', 'FIT2102_L2', 'FIT3143_T4', 'FIT3143_T3', 'FIT3143_T2', 'FIT3143_T1',
             'FIT3162_L1', 'FIT3081_L2', 'FIT3081_L1', 'FIT3155_T1', 'FIT3155_T2', 'FIT3155_T3', 'FIT3155_T4',
             'FIT3161_L1', 'FIT2004_L1', 'FIT2004_L2', 'FIT2102_T1', 'FIT2102_T3', 'FIT2102_T2', 'FIT3081_T2',
             'FIT3143_L2', 'FIT3143_L1', 'FIT3081_T1']

# for unit in all_units:
#     print(unit, analysis_algo(unit))