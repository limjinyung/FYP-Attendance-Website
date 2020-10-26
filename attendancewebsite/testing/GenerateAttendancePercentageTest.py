import unittest
from attendancewebsite import service
from unittest.mock import Mock
from datetime import datetime
from freezegun import freeze_time


class GenerateAttendancePercentageTest(unittest.TestCase):

    def test_generate_attendance_total_percentage(self):
        """
        The test suite is written to test the function, generate_attendance_total_percentage
        """
        # This test case is to test if the function is able to calculate the overall percentage 
        # (from week 1 till week “X” where X is the current week) for each of the units a student is taking in the current semester.
        attendance_sheet = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        student_attendance_week_list = {'FIT3081_L2': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'FIT3081_T1': [1, 3, 4, 5, 6, 7, 9, 10, 11, 12],
        'FIT2102_L1': [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12]}
        expected_output = {'FIT3081_L2': 100.0, 'FIT3081_T1': 83.33, 'FIT2102_L1': 91.67}
        actual_output = service.generate_attendance_total_percentage(attendance_sheet, student_attendance_week_list)
        self.assertEqual(expected_output, actual_output)

    def test_generate_attendance_percentage(self):
        """
        The test suite is written to test the function, generate_attendance_percentage
        """
        # This test case is to test if the function will return student’s every week unit's attendance percentage
        # by dividing student's every unit week list with attendance sheet week list
        attendance_sheet = [1, 2, 3, 4, 5]
        student_attendance_week_list = {'FIT3155_L1': [2, 4, 6], 'FIT3081_L1': [1, 2, 3, 4, 5], 'FIT3081_T1': [1, 2, 3, 4], 'FIT3155_T1': [1, 3, 4]}
        expected_output = {'FIT3081_L1': [100.0, 100.0, 100.0, 100.0, 100.0], 'FIT3081_T1': [100.0, 100.0, 100.0, 100.0, 80.0], 
        'FIT3155_L1': [0.0, 50.0, 33.33, 50.0, 40.0], 'FIT3155_T1': [100.0, 50.0, 66.67, 75.0, 60.0]}
        actual_output = service.generate_attendance_percentage(attendance_sheet, student_attendance_week_list)
        self.assertEqual(expected_output, actual_output)

    def test_calculate_unit_attendance(self):
        """
        The test suite is written to test the function, calculate_unit_attendance
        """
        # This test case is to test if the function is able to calculate the unit weekly attendance by
        # comparing weekly student’s attendance list with
        # attendance sheet and the student’s attendance list that was supposed to be retrieved from the database
        # will be mocked using a Python object.
        mock_db = Mock()
        
        mock_db.session.query.return_value.filter.return_value.filter.return_value.filter.return_value.all.return_value = [
            ('29036186', 'FIT3155_L1', '2020', '2'), ('29821894', 'FIT3155_L1', '2020', '2')]
        
        attendance_list = [
            ('29036186', 'FIT3081_L1', 1, datetime(2020, 8, 3, 10, 10), datetime(2020, 8, 3, 12, 0), False, '2020', '2'), 
            ('29036186', 'FIT3081_L1', 2, datetime(2020, 8, 10, 10, 2), datetime(2020, 8, 10, 12, 1), False, '2020', '2')
            ]
        unit_code = "FIT3155_L1"
        mock_student_unit = Mock()
        mock_student_unit.c.return_value.unit_code.return_value = "FIT3155_L1"
        mock_student_unit.c.return_value.year.return_value = "2020"
        mock_student_unit.c.return_value.semester.return_value = "2"
        this_year = "2020"
        this_semester = "2"
        start_week = datetime(2020, 8, 3)

        with freeze_time("2020-9-1"):
            expected_output = {1: 50.0, 2: 50.0, 3: 0.0, 4: 0.0}
            actual_output = service.calculate_unit_attendance(attendance_list, unit_code, mock_db, mock_student_unit, this_year, this_semester, start_week)
            self.assertEqual(expected_output, actual_output)


def main():
    # Create the test suite from the cases above.
    suite = unittest.TestLoader().loadTestsFromTestCase(GenerateAttendancePercentageTest)
    # This will run the test suite.
    unittest.TextTestRunner(verbosity=3).run(suite)


main()