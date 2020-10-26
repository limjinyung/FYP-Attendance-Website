import unittest
from attendancewebsite import service
from datetime import datetime
from freezegun import freeze_time


class ServiceTest(unittest.TestCase):
    
    def test_find_this_week(self):
        """
        The test suite is written to test the function, find_this_week
        """
        # This test case is to test when the chosen date falls on the 1st week of the current semester
        with freeze_time("2020-08-06"):
            start_date = datetime(2020, 8, 3)
            expected_output = 1
            actual_output = service.find_this_week(start_date)
            self.assertEqual(expected_output, actual_output)
        
        # This test case is to test when the chosen date falls on the 7th week of the current semester
        with freeze_time("2020-09-17"):
            start_date = datetime(2020, 8, 3)
            expected_output = 7
            actual_output = service.find_this_week(start_date)
            self.assertEqual(expected_output, actual_output)

        # This test case is to test when the chosen date falls on the 11th week of the current semester. 
        # This doesn’t take the mid-semester break into account.
        with freeze_time("2020-10-15"):
            start_date = datetime(2020, 8, 3)
            expected_output = 11
            actual_output = service.find_this_week(start_date)
            self.assertEqual(expected_output, actual_output)

    def test_get_unit(self):
        """
        The test suite is written to test the function, get_unit
        """
        # This test case is to test when an empty list is passed to function as an argument.
        attendance_list = []
        expected_output = []
        actual_output = service.get_unit(attendance_list)
        self.assertEqual(expected_output, actual_output)
        
        # This test case is to test when an attendance list containing only one single unit is passed to the function as an argument.
        attendance_list = [
            ('29036186', 'FIT3081_L1', 1, datetime(2020, 8, 3, 10, 10), datetime(2020, 8, 3, 12, 0), False, '2020', '2')
            ]
        expected_output = ["FIT3081_L1"]
        actual_output = service.get_unit(attendance_list)
        self.assertEqual(expected_output, actual_output)

        # This test case is to test when an attendance_list containing 2 repeated units is passed into the function as an argument.
        attendance_list = [
            ('29036186', 'FIT3081_L1', 1, datetime(2020, 8, 3, 10, 10), datetime(2020, 8, 3, 12, 0), False, '2020', '2'),
            ('29036186', 'FIT3081_L1', 1, datetime(2020, 8, 3, 10, 10), datetime(2020, 8, 3, 12, 0), False, '2020', '2')
            ]
        expected_output = ["FIT3081_L1"]
        actual_output = service.get_unit(attendance_list)
        self.assertEqual(expected_output, actual_output)

    def test_create_attendance_sheet(self):
        """
        The test suite is written to test the function, create_attendance_sheet
        """
        # This test case is to test if the function will return two lists of week lists containing
        # from week 1 to week “X” correctly if the chosen week is week 10.
        with freeze_time("2020-10-15"):
            start_date = datetime(2020, 8, 3)
            week_before_semester = 7
            expected_output = ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10'])
            actual_output = service.create_attendance_sheet(start_date, week_before_semester)
            self.assertEqual(expected_output, actual_output)

    def test_student_attendance_week(self):
        """
        The test suite is written to test the function, student_attendance_week
        """
        # This test case is to test if the function can retrieve the week element of the attendance list
        # passed into the function as an argument.
        attendance_list = [
            ('29036186', 'FIT3081_L1', 1, datetime(2020, 8, 3, 10, 10), datetime(2020, 8, 3, 12, 0), False, '2020', '2')
            ]
        expected_output = [1]
        actual_output = service.student_attendance_week(attendance_list)
        self.assertEqual(expected_output, actual_output)

        # This test case is to test when an empty list is passed to function as an argument.
        attendance_list = []
        expected_output = []
        actual_output = service.student_attendance_week(attendance_list)
        self.assertEqual(expected_output, actual_output)

    def test_sort_unit(self):
        """
        The test suite is written to test the function, sort_unit
        """
        # This test case is to test if the function is able to sort the attendance_list by units and return the sorted attendance_list.
        units = ['FIT3081_L1', 'FIT3081_T1']
        attendance_list = [('29036186', 'FIT3081_L1', 1, datetime(2020, 8, 3, 10, 10), datetime(2020, 8, 3, 12, 0), False, '2020', '2'), 
        ('29036186', 'FIT3081_T1', 2, datetime(2020, 8, 10, 10, 2), datetime(2020, 8, 10, 12, 1), False, '2020', '2')]
        expected_output = {'FIT3081_L1': [1], 'FIT3081_T1': [2]}
        actual_output = service.sort_unit(units, attendance_list)
        self.assertEqual(expected_output, actual_output)

    def test_extract_units(self):
        """
        The test suite is written to test the function, extract_units
        """
        # This test case is to test if the function is able to only return the modified attendance list 
        # that only contains the units specified by the selected units passed into the function as an argument.
        selected_units = ['FIT3081_L1']
        attendance_list = [
            ('29036186', 'FIT3081_L1', 1, datetime(2020, 8, 3, 10, 10), datetime(2020, 8, 3, 12, 0), False, '2020', '2'),
            ('29036186', 'FIT3081_T1', 1, datetime(2020, 8, 3, 14, 10), datetime(2020, 8, 3, 15, 0), False, '2020', '2')
            ]
        expected_output = [
            ('29036186', 'FIT3081_L1', 1, datetime(2020, 8, 3, 10, 10), datetime(2020, 8, 3, 12, 0), False, '2020', '2')
            ]
        actual_output = service.extract_units(attendance_list, selected_units)
        self.assertEqual(expected_output, actual_output)

    def test_attendance_data_without_sid(self):
        """
        The test suite is written to test the function, attendance_data_without_sid
        """
        # This test case is to test if the function is able to return the caller with the modified attendance_list with the student id removed.
        attendance_list = [
            ('29036186', 'FIT3081_L1', 1, datetime(2020, 8, 3, 10, 10), datetime(2020, 8, 3, 12, 0), False, '2020', '2'), 
            ('29036186', 'FIT3081_L1', 2, datetime(2020, 8, 10, 10, 2), datetime(2020, 8, 10, 12, 1), False, '2020', '2')
            ]
        
        expected_output = [
            ['FIT3081_L1', 1, datetime(2020, 8, 3, 10, 10), datetime(2020, 8, 3, 12, 0), False, '2020', '2'], 
            ['FIT3081_L1', 2, datetime(2020, 8, 10, 10, 2), datetime(2020, 8, 10, 12, 1), False, '2020', '2']
            ]
        actual_output = service.attendance_data_without_sid(attendance_list)
        self.assertEqual(expected_output, actual_output)


def main():
    # Create the test suite from the cases above.
    suite = unittest.TestLoader().loadTestsFromTestCase(ServiceTest)
    # This will run the test suite.
    unittest.TextTestRunner(verbosity=3).run(suite)


main()
