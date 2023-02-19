from apps.home import blueprint
from flask import render_template, Response, current_app
from apps.home.util import (
                                get_all_data_for_course_categories,
                                get_course_bundle_count,
                                get_course_data_for_category,
                                get_course_details,
                                getFileFromS3
                        )

from apps import mysqlDB, mongoDB

@blueprint.route('/', methods=['GET'])
def index():
    try:
        categoryData = get_all_data_for_course_categories(mongodb=mongoDB)
        bundlecount = get_course_bundle_count(mongodb=mongoDB)
        return render_template('home/index.html',categorydata = categoryData, 
                                                    bundlecount = bundlecount,
                                                    zip=zip)
    except Exception as err:
        current_app.logger.exception(err)
        return render_template('home/page-404.html')
        
@blueprint.route('/category-courses/<string:categoryId>', methods=['GET'])
def category_courses(categoryId):
    try:
        course_result, bundle_count = get_course_data_for_category(categoryId=categoryId, mongodb=mongoDB)
        if(len(course_result) == 0):
            return render_template('home/courses_not_found.html')
        return render_template('home/category_courses.html', coursesdata = course_result, bundlecount = bundle_count)
    except Exception as err:
        current_app.logger.exception(err)
        return render_template('home/page-404.html')

@blueprint.route('/course/<string:course_name>', methods=['GET'])
def course_details(course_name):
    try:
        course_data = get_course_details(course_name=course_name, mongodb=mongoDB)
        return render_template('home/course.html', coursedata = course_data)
    except Exception as err:
        current_app.logger.exception(err)
        return render_template('home/page-404.html')

@blueprint.route('/download/<string:coursename>', methods=['GET'])
def download_file_from_s3(coursename):
    try:
        file = getFileFromS3(coursename)
        return Response(
            file['Body'].read(),
            mimetype='application/pdf',
            headers={"Content-Disposition": f"attachment;filename={coursename.replace(' ','-')}.pdf"}
        )
    except Exception as err:
        current_app.logger.exception(err)
        return render_template('home/page-404.html')