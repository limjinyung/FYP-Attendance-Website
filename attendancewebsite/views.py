from flask_appbuilder.charts.views import DirectByChartView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from attendancewebsite.models import Student

class StudentTable(DirectByChartView):
    datamodel = SQLAInterface(Student)
    chart_title = 'Student Attendance'

    definitions = [{
        'label': 'Attendance',
        'group': 'unit_code',
        'series':['time_in', 'time_out']
    }]