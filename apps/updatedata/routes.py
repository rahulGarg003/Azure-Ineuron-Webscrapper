from apps.updatedata import blueprint
import os
from flask import render_template, request, current_app, redirect, url_for
# from decouple import config
from apps.updatedata.util import (
                                    get_category_data, 
                                    insert_course_bundle_count_by_category,
                                    insert_data_for_categories,
                                    insert_data_for_courses,
                                    insert_course_description_data,
                                    generateCoursePdf,
                                    uploadToS3,
                                    get_all_courses,
                                    get_course_detailed_data,
                                    insert_course_bundle_count
                                )

from apps import mysqlDB, mongoDB

@blueprint.route('/update-data', methods = ['GET', 'POST'])
def update_data():
    if(request.method == 'POST'):
        if(request.form['password-update'] == os.environ.get('APP_UPDATE_PASSWORD')):
            if(os.environ['isUpdateDataCalled'] == 'False'):
                try:
                    os.environ['isUpdateDataCalled'] = 'True'
                    #scrap category data
                    category_data = get_category_data()

                    #insert data to mongodb
                    for data in category_data:
                        insert_data_for_categories(data,mongodb=mongoDB)

                    #scrap course data
                    # course_data_bundle = get_course_details_data()
                    # course_data = course_data_bundle['course-data']
                    # course_bundle_count_by_category = course_data_bundle['course-bundle-count-by-category']

                    bundles_count = {}
                    bundle_count_by_category = {}
                    for course in get_all_courses():
                        course_data = get_course_detailed_data(course)
                        bundle_name = course_data['course-bundle-name']
                        category_id = course_data['course-category-id']
                        if(bundle_name in bundles_count):
                            bundles_count[bundle_name] = bundles_count[bundle_name] + 1
                        else:
                            bundles_count[bundle_name] = 1
                        if(category_id in bundle_count_by_category):
                            if(bundle_name in bundle_count_by_category[category_id]):
                                bundle_count_by_category[category_id][bundle_name] = bundle_count_by_category[category_id][bundle_name] + 1
                            else:
                                bundle_count_by_category[category_id][bundle_name] = 1
                        else:
                            bundle_count_by_category[category_id] = {}
                            bundle_count_by_category[category_id][bundle_name] = 1
                        
                        #insert data to mongodb, mysql and generate pdfs
                        insert_data_for_courses(course_data, mongodb=mongoDB)
                        insert_course_description_data(course_data, mysqldb=mysqlDB)
                        pdfByteString = generateCoursePdf(course_data, savePdf=False)
                        uploadToS3(fileName=course_data['course-name'], pdfString=pdfByteString, isSavedPdf=False)
                        current_app.logger.info(f"Data successfully updated for {course_data['course-name']}")

                    #insert data to mongodb, mysql and generate pdfs
                    # for data in course_data:
                    #     insert_data_for_courses(data, mongodb=mongoDB)
                    #     print('mongo course')
                    #     insert_course_description_data(data, mysqldb=mysqlDB)
                    #     print('mysql course')
                    #     pdfByteString = generateCoursePdf(data, savePdf=False)
                    #     uploadToS3(fileName=data['course-name'], pdfString=pdfByteString, isSavedPdf=False)
                    #     print('pdf upload')
                    
                    for key, value in bundle_count_by_category.items():
                        insert_course_bundle_count_by_category(key, value, mongodb=mongoDB)
                    for key, value in bundles_count.items():
                        insert_course_bundle_count(key, value, mongodb=mongoDB)
                    current_app.logger.info('Data Successfully Updated')
                    os.environ['isUpdateDataCalled'] = 'False'
                    return redirect(url_for('home_blueprint.index'), 200)
                except Exception as err:
                    current_app.logger.exception(err)
                    os.environ['isUpdateDataCalled'] = 'False'
                    return render_template('home/page-404.html')
            else:
                return render_template('home/login.html', msg="Process already running please wait!!!")
        else:
            return render_template('home/login.html', msg="Wrong Password! Please provide correct password")
    else:
        return render_template('home/login.html')