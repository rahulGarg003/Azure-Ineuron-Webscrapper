# from decouple import config
import secrets
from sys import exit
from dotenv import load_dotenv
import os

class Config(object):

    #setup App Secret Key
    SECRET_KEY = secrets.token_hex(20)
    load_dotenv()

class ProductionConfig(Config):

    #set debug flag
    DEBUG = False
    try:
        # a = config['AWS_S3_REGION_NAME']
        # a = config['AWS_S3_BUCKET_NAME']
        # a = config['AWS_ACCESS_KEY_ID']
        # a = config['AWS_SECRET_ACCESS_KEY']
        # a = config['MONGO_DB_COLL_COURSE']
        # a = config['MONGO_DB_COLL_CATEGORY']
        # a = config['MONGO_DB_COLL_COURSE_BNDL_CNT_CATGRY']
        # a = config['MONGO_DB_COLL_COURSE_BNDL_CNT']
        # a = config['APP_UPDATE_PASSWORD']
        os.environ.get('AWS_S3_REGION_NAME')
        os.environ.get('AWS_S3_BUCKET_NAME')
        os.environ.get('AWS_ACCESS_KEY_ID')
        os.environ.get('AWS_SECRET_ACCESS_KEY')
        os.environ.get('MONGO_DB_COLL_COURSE')
        os.environ.get('MONGO_DB_COLL_CATEGORY')
        os.environ.get('MONGO_DB_COLL_COURSE_BNDL_CNT_CATGRY')
        os.environ.get('MONGO_DB_COLL_COURSE_BNDL_CNT')
        os.environ.get('APP_UPDATE_PASSWORD')
        # SQLALCHEMY_DATABASE_URI = '{}+pymysql://{}:{}@{}:{}/{}'.format(
        #     config('SQL_DB_ENGINE'),
        #     config('SQL_DB_USERNAME'),
        #     config('SQL_DB_PASSWORD'),
        #     config('SQL_DB_HOSTNAME'),
        #     config('SQL_DB_PORT'),
        #     config('SQL_DB_NAME')
        # )
        SQLALCHEMY_DATABASE_URI = '{}+pymysql://{}:{}@{}:{}/{}'.format(
            os.environ.get('SQL_DB_ENGINE'),
            os.environ.get('SQL_DB_USERNAME'),
            os.environ.get('SQL_DB_PASSWORD'),
            os.environ.get('SQL_DB_HOSTNAME'),
            os.environ.get('SQL_DB_PORT'),
            os.environ.get('SQL_DB_NAME')
        )
        # MONGO_URI = 'mongodb+srv://{}:{}@{}/{}?retryWrites=true&w=majority'.format(
        #     config('MONGO_DB_USERNAME'),
        #     config('MONGO_DB_PASSWORD'),
        #     config('MONGO_DB_HOSTNAME'),
        #     config('MONGO_DB_NAME')
        # )
        MONGO_URI = 'mongodb+srv://{}:{}@{}/{}?retryWrites=true&w=majority'.format(
            os.environ.get('MONGO_DB_USERNAME'),
            os.environ.get('MONGO_DB_PASSWORD'),
            os.environ.get('MONGO_DB_HOSTNAME'),
            os.environ.get('MONGO_DB_NAME')
        )
    except KeyError as e:
        exit(f'Please provide DB credentials: {e}')

config_dict = {
    'Production' : ProductionConfig
}