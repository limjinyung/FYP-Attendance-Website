import unittest
from attendancewebsite import service
from unittest.mock import Mock, patch
from datetime import time


class DataAnalyticTest(unittest.TestCase):
    @patch('attendancewebsite.service.get_possible_class_start_time')    
    def test_get_class_start_time(self, mock_obj):
        """
        The test suite is written to test the function, get_class_start_time
        """
        # This test case is to test when the class start time of the unit code passed into the function is between 0800
        # (inclusive) and 1000 (exclusive).
        # The club start time of the unit code is changed to be too early through mocking to stimulate the particular scenario.

        mock_db = Mock()
        mock_db.session.query.return_value.filter.return_value.all.return_value = [("CS001", "FIT3155_L1", time(9, 0, 0))]

        mock_obj.return_value = ["12:00:00", "14:00:00"]

        unit_code = "FIT3155_L1"
        mock_room_unit = Mock()
        mock_room_unit.c.return_value.unit_code = "FIT3155_L1"
        mock_Club = Mock()
        
        
        expected_output = (True, ["12:00:00", "14:00:00"])
        actual_output = service.get_class_start_time(unit_code, mock_db, mock_room_unit, mock_Club)
        self.assertEqual(expected_output, actual_output)

        # This test case is to test when the class start time of the unit code passed into the function is after 1800 (inclusive). 
        # The class start time is changed to too late through mocking to stimulate the particular scenario.
        mock_db.session.query.return_value.filter.return_value.all.return_value = [("CS001", "FIT3155_L1", time(18, 0, 0))]
        expected_output = (True, ["12:00:00", "14:00:00"])
        actual_output = service.get_class_start_time(unit_code, mock_db, mock_room_unit, mock_Club)
        self.assertEqual(expected_output, actual_output)

        # This test case  is to test when the class start time of the unit code passed into the function is between
        # 1000 (inclusive) and 1800 (exclusive).
        # The class start time is changed to be just right through mocking to stimulate the particular scenario.
        mock_db.session.query.return_value.filter.return_value.all.return_value = [("CS001", "FIT3155_L1", time(15, 0, 0))]
        expected_output = (False, [])
        actual_output = service.get_class_start_time(unit_code, mock_db, mock_room_unit, mock_Club)
        self.assertEqual(expected_output, actual_output)

    def test_get_possible_class_start_time(self):
        """
        The test suite is written to test the function, get_possible_class_start_time
        """
        # This test case is to test if the function is able to handle the scenario where none of the possible
        # class start time is clashing with any clubs. This is stimulated through mocking.
        # The Possible Class Start Time is 14:00:00

        mock_db = Mock()
        mock_db.session.query.return_value.filter.return_value.all.return_value = [
            ("CS001", "FIT3155_L1", time(8, 0, 0), 3600, "Monday"),
            ("CS001", "FIT2107_L1", time(13, 0, 0), 3600, "Monday")
        ]

        unit_code = "FIT3155_L1"

        room_unit = Mock()
        room_unit.c.return_value.unit_code = "FIT3155_L1"
        room_unit.c.return_value.day = "Monday"

        mock_Club = Mock()

        mock_club = Mock()
        mock_club.day = "Monday"
        mock_club.club_start_time.hour = 15
        mock_club.club_start_time.minute = 0
        mock_club.club_start_time.second = 0
        mock_club.club_duration = 3600
        mock_db.session.query.return_value.all.return_value = [
            mock_club
        ]

        expected_output = ['14:00:00']
        actual_output = service.get_possible_class_start_time(unit_code, mock_db, room_unit, mock_Club)
        self.assertEqual(expected_output, actual_output)

        # This test case is to test if the function is able to handle the scenario where one of the
        # possible class start times is clashing with one club.
        # The club start time happens when the class is on-going. This is stimulated through mocking.
        # The Possible Class Start Time is 14:00:00
        mock_club = Mock()
        mock_club.day = "Monday"
        mock_club.club_start_time.hour = 14
        mock_club.club_start_time.minute = 30
        mock_club.club_start_time.second = 0
        mock_club.club_duration = 3600
        mock_db.session.query.return_value.all.return_value = [
            mock_club
        ]
        expected_output = []
        actual_output = service.get_possible_class_start_time(unit_code, mock_db, room_unit, mock_Club)
        self.assertEqual(expected_output, actual_output)
        
        # This test case is to test if the function is able to handle the scenario where one of the
        # possible class start times is clashing with one club.
        # The club is still on going when the class has just started. This is stimulated through mocking.
        # The Possible Class Start Time is 14:00:00
        mock_club = Mock()
        mock_club.day = "Monday"
        mock_club.club_start_time.hour = 13
        mock_club.club_start_time.minute = 00
        mock_club.club_start_time.second = 0
        mock_club.club_duration = 7200
        mock_db.session.query.return_value.all.return_value = [
            mock_club
        ]
        expected_output = []
        actual_output = service.get_possible_class_start_time(unit_code, mock_db, room_unit, mock_Club)
        self.assertEqual(expected_output, actual_output)
        
    def test_get_clubs_datetime(self):
        """
        The test suite is written to test the function, get_clubs_datetime
        """
        # This test case is to test if the function is able to handle the scenario where none of the club start time
        # is clashing with the class start time.
        # This is stimulated through mocking.
        mock_db = Mock()
        mock_db.session.query.return_value.filter.return_value.all.return_value = [
            ("CS001", "FIT3155_L1", time(14, 0, 0), 3600, "Monday")
        ]
        unit_code = "FIT3155_L1"
        room_unit = Mock()
        room_unit.c.return_value.unit_code = "FIT3155_L1"
        
        mock_Club = Mock()

        mock_club = Mock()
        mock_club.club_name = "Chinese Club"
        mock_club.club_code = "0001"
        mock_club.day = "Monday"
        mock_club.club_start_time.hour = 13
        mock_club.club_start_time.minute = 00
        mock_club.club_start_time.second = 0
        mock_club.club_duration = 3600
        mock_db.session.query.return_value.all.return_value = [
            mock_club
        ]
        
        expected_output = []
        actual_output = service.get_clubs_datetime(unit_code, mock_db, room_unit, mock_Club)
        self.assertEqual(expected_output, actual_output)

        # This test case is to test if the function is able to handle the scenario where one of the club start times
        # is clashing with the class start time.
        # The club start time happens when the class is on-going. This is stimulated through mocking.
        mock_club = Mock()
        mock_club.club_name = "Chinese Club"
        mock_club.club_code = "0001"
        mock_club.day = "Monday"
        mock_club.club_start_time.hour = 14
        mock_club.club_start_time.minute = 30
        mock_club.club_start_time.second = 0
        mock_club.club_duration = 3600
        mock_db.session.query.return_value.all.return_value = [
            mock_club
        ]

        expected_output = [["Chinese Club", "0001", -1800]]
        actual_output = service.get_clubs_datetime(unit_code, mock_db, room_unit, mock_Club)
        self.assertEqual(expected_output, actual_output)

        # This test case is to test if the function is able to handle the scenario where one of the club start times
        # is clashing with the class start time.
        # The club is still on going when the class has just started. This is stimulated through mocking.
        mock_club = Mock()
        mock_club.club_name = "Chinese Club"
        mock_club.club_code = "0001"
        mock_club.day = "Monday"
        mock_club.club_start_time.hour = 13
        mock_club.club_start_time.minute = 30
        mock_club.club_start_time.second = 0
        mock_club.club_duration = 3600
        mock_db.session.query.return_value.all.return_value = [
            mock_club
        ]

        expected_output = [["Chinese Club", "0001", 1800]]
        actual_output = service.get_clubs_datetime(unit_code, mock_db, room_unit, mock_Club)
        self.assertEqual(expected_output, actual_output)

    def test_retake_num_of_students(self):
        """
        The test suite is written to test the function, retake_num_of_students
        """
        # This test case is to test if the function is able to handle the scenario where one of
        # the students taking the unit, FIT3155_L1 has retaken the unit before and is currently taking the unit.
        # This is achieved through mocking since this  list will be retrieved from the database.
        mock_db = Mock()
        mock_db.session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            ("29821894", "2020", "2"), ("29821894", "2019", "2"), ("1234567", "2020", "2")
        ]
        unit_code = "FIT3155_L1"
        year = "2020"
        sem = "2"
        mock_student_unit = Mock()
        mock_student_unit.c.return_value.student_id.asc.return_value = None
        mock_student_unit.c.return_value.student_id = None
        mock_student_unit.c.return_value.year = "2020"
        mock_student_unit.c.return_value.semester = "2"
        mock_student_unit.c.return_value.unit_code = "FIT3155_L1"
        expected_output = 1

        actual_output = service.retake_num_of_students(unit_code, year, sem, mock_db, mock_student_unit)
        self.assertEqual(expected_output, actual_output)

        # This test case is to test if the function is able to handle the scenario where one of the students
        # taking the unit, FIT3155_L1 has retaken the unit before and is not currently taking the unit.
        # This is achieved through mocking since this list will be retrieved from the database.
        mock_db.session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            ("29821894", "2020", "1"), ("29821894", "2019", "2"), ("1234567", "2020", "2")
        ]
        expected_output = 0
        actual_output = service.retake_num_of_students(unit_code, year, sem, mock_db, mock_student_unit)
        self.assertEqual(expected_output, actual_output)

        # This test case is to test if the function is able to handle the scenario where none of the students
        # taking the unit, FIT3155_L1 has retaken the unit before.
        # This is achieved through mocking since this list will be retrieved from the database.
        mock_db.session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            ("29821894", "2020", "2"), ("1234567", "2020", "2")
        ]
        expected_output = 0
        actual_output = service.retake_num_of_students(unit_code, year, sem, mock_db, mock_student_unit)
        self.assertEqual(expected_output, actual_output)

    def test_analysis_algo(self):
        """
        The test suite is written to test the function, analysis_algo
        """
        mock_db = Mock()
        mock_db.session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            ("29821894", "2020", "2"), ("29821894", "2019", "2"), ("1234567", "2020", "2")
        ]
        mock_db.session.query.return_value.filter.return_value.all.return_value = [("CS001", "FIT3155_L1", time(9, 0, 0))]
        mock_db.session.query.return_value.filter.return_value.all.return_value = [
            ("CS001", "FIT3155_L1", time(8, 0, 0), 3600, "Monday"),
            ("CS001", "FIT2107_L1", time(13, 0, 0), 3600, "Monday")
        ]

        unit_code = "FIT3155_L1"
        year = "2020"
        sem = "2"

        mock_student_unit = Mock()
        mock_student_unit.c.return_value.year = "2020"
        mock_student_unit.c.return_value.semester = "2"
        mock_student_unit.c.return_value.unit_code = "FIT3155_L1"

        mock_student_club = Mock()
        mock_student_club.c.return_value.club = "0001"

        room_unit = Mock()
        room_unit.c.return_value.unit_code = "FIT3155_L1"

        mock_weather = Mock()
        mock_weather.weather = 'Sunny'
        mock_db.session.query.return_value.filter.return_value.filter.return_value.filter.return_value.all.return_value = [mock_weather]

        mock_club = Mock()
        mock_club.club_name = "Chinese Club"
        mock_club.club_code = "0001"
        mock_club.day = "Monday"
        mock_club.club_start_time.hour = 13
        mock_club.club_start_time.minute = 00
        mock_club.club_start_time.second = 0
        mock_club.club_duration = 3600
        mock_db.session.query.return_value.all.return_value = [
            mock_club
        ]

        # This test case is to test when the class start time of the unit code is  the only factor affecting
        # the low attendance rate and all the other factors are irrelevant in this scenario.
        expected_output = {
            'analysis_suggestion': "Please choose another class time if there's any other time slots available",
            'class_start_time_analysis': (True, []),
            'club_clash_analysis': (False, [], []),
            'student_retake_analysis': (False, 0, 0),
            'weather_analysis': (False, 0, [mock_weather])}
        actual_output = service.analysis_algo(unit_code, mock_db, room_unit, mock_student_unit, mock_student_club, year, 
                                              sem, mock_weather, mock_club)
        self.assertEqual(expected_output, actual_output)

        # This test case is to test when there’s no factor affecting the low attendance rate.
        mock_db.session.query.return_value.filter.return_value.all.return_value = [("CS001", "FIT3155_L1", time(15, 0, 0), 3600, "Monday")]
        expected_output = {
            'analysis_suggestion': "Class is good!",
            'class_start_time_analysis': (False, []),
            'club_clash_analysis': (False, [], []), 
            'student_retake_analysis': (False, 0, 0),
            'weather_analysis': (False, 0, [mock_weather])}
        actual_output = service.analysis_algo(unit_code, mock_db, room_unit, mock_student_unit, mock_student_club, year,
                                              sem, mock_weather, mock_club)
        self.assertEqual(expected_output, actual_output)

        # This test case is to test when the weather is the only factor affecting the low attendance rate 
        # and all the other factors are irrelevant in this scenario.
        mock_weather.weather = 'Thunderstorm'
        expected_output = {
            'analysis_suggestion': "It's always bad weather when your class starts. "
                                   "We're sorry but we don't have the ability to control weather right now.",
            'class_start_time_analysis': (False, []),
            'club_clash_analysis': (False, [], []), 'student_retake_analysis': (False, 0, 0),
            'weather_analysis': (True, 100.0, [mock_weather])}
        actual_output = service.analysis_algo(unit_code, mock_db, room_unit, mock_student_unit, mock_student_club, year,
                                              sem, mock_weather, mock_club)
        self.assertEqual(expected_output, actual_output)


def main():
    # Create the test suite from the cases above.
    suite = unittest.TestLoader().loadTestsFromTestCase(DataAnalyticTest)
    # This will run the test suite.
    unittest.TextTestRunner(verbosity=3).run(suite)


main()