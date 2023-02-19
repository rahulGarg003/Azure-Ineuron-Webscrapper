import boto3
from apps.updatedata.models import ScrappedCourseData
# from decouple import config
import os

def get_all_data_for_course_categories(mongodb):
    db = mongodb.db
    data = db[os.environ.get('MONGO_DB_COLL_CATEGORY')].find()
    cat_data = []
    for i in data:
        cat_data.append(i.get('category-data'))
    return cat_data

def get_course_bundle_count(mongodb):
    db = mongodb.db
    data = db[os.environ.get('MONGO_DB_COLL_COURSE_BNDL_CNT')].find()
    return [i for i in data]

def get_course_data_for_category(categoryId, mongodb):
    courses = ScrappedCourseData.query.filter_by(category_id=categoryId).all()
    course_result = []
    for num, crs in enumerate(courses):
        courseno = num+1
        coursename = crs.course_name
        courselanguage = crs.course_language
        coursemode = crs.course_mode
        coursebundlename = crs.course_bundle_name
        coursedescription = crs.course_description
        course_result.append((courseno, coursename, coursedescription, courselanguage, coursemode, coursebundlename))
    bundle_count = mongodb.db[os.environ.get('MONGO_DB_COLL_COURSE_BNDL_CNT_CATGRY')].find_one({'_id':categoryId})
    if(bundle_count == None):
        return (course_result, None)
    return (course_result, bundle_count.get('category-bundle-count'))

def get_course_details(course_name, mongodb):
    course = mongodb.db[os.environ.get('MONGO_DB_COLL_COURSE')].find_one({'_id' : course_name})
    return course['course-data']

def getFileFromS3(fileName: str):
    s3 = boto3.resource(
            service_name = 's3',
            region_name = os.environ.get('AWS_S3_REGION_NAME'),
            aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
    bucketName = os.environ.get('AWS_S3_BUCKET_NAME')
    # s3.Bucket(bucketName).download_file(Key = fileName.replace(' ','-'), Filename = fileName.replace(' ','-'))
    file = s3.Object(bucketName, f"{fileName.replace(' ','-')}.pdf").get()
    return file