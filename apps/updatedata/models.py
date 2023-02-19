from apps import mysqlDB
from datetime import datetime

class ScrappedCourseData(mysqlDB.Model):
    course_id = mysqlDB.Column(mysqlDB.String(100), primary_key=True)
    course_name = mysqlDB.Column(mysqlDB.String(200), nullable=False)
    course_description = mysqlDB.Column(mysqlDB.String(10000), nullable=False)
    course_bundle_name = mysqlDB.Column(mysqlDB.String(100), nullable=False)
    course_language = mysqlDB.Column(mysqlDB.String(100), nullable=False)
    course_mode = mysqlDB.Column(mysqlDB.String(100), nullable=False)
    category_id = mysqlDB.Column(mysqlDB.String(100), nullable=False)