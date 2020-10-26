import unittest
from attendancewebsite import service
from datetime import datetime


class LateAbsentDataTest(unittest.TestCase):

    def test_calculate_late_data(self):
        """
        The test suite is written to test the function, calculate_late_data
        """
        # This test function is to test if the function is able to return the late attendance percentage together with the tuple 
        # (containing the week and the time where the student is late to the class) in the attendance list.
        week_list = [1, 2]
        attendance_list = [
            ('29036186', 'FIT3081_L1', 1, datetime(2020, 8, 3, 10, 10), datetime(2020, 8, 3, 12, 0), True, '2020', '2'), 
            ('29036186', 'FIT3081_L1', 2, datetime(2020, 8, 10, 10, 2), datetime(2020, 8, 10, 12, 1), False, '2020', '2')
            ]
        expected_output = (50.0, [[1, '08/03/2020, 10:10:00', '08/03/2020, 12:00:00']])
        actual_output = service.calculate_late_data(week_list, attendance_list)
        self.assertEqual(expected_output, actual_output)

    def test_calculate_absent_date(self):
        """
        The test suite is written to test the function, calculate_absent_date
        """
        # This test function is to test if the function is able to return the absent attendance percentage together with the tuple 
        # (containing the week and the time where the student is absent to the class) in the attendance list. 
        week_list = [1, 2, 3, 4, 5]
        attendance_list = [
            ('29036186', 'FIT3081_L1', 1, datetime(2020, 8, 3, 10, 10), datetime(2020, 8, 3, 12, 0), False, '2020', '2'), 
            ('29036186', 'FIT3081_L1', 2, datetime(2020, 8, 10, 10, 2), datetime(2020, 8, 10, 12, 1), False, '2020', '2')
            ]
        start_week = datetime(2020, 8, 3)
        expected_output = (60.0, [[3, '05/08/2020'], [4, '06/08/2020'], [5, '07/08/2020']])
        actual_output = service.calculate_absent_data(week_list, attendance_list, start_week)
        self.assertEqual(expected_output, actual_output)


def main():
    # Create the test suite from the cases above.
    suite = unittest.TestLoader().loadTestsFromTestCase(LateAbsentDataTest)
    # This will run the test suite.
    unittest.TextTestRunner(verbosity=3).run(suite)


main()