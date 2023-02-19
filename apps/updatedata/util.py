import json
import requests
from bs4 import BeautifulSoup as bs
from apps.updatedata.models import ScrappedCourseData
from fpdf import FPDF
import os
import boto3
# from decouple import config

def get_url(route='',page_type='home'):
    base_url = 'https://www.ineuron.ai'
    if(page_type.lower() == 'course'):
        return base_url + '/course/' + route.replace(' ', '-')
    elif(page_type.lower() == 'category'):
        return base_url + '/category/' + route.replace(' ', '-')
    return base_url

def get_script_data(route='', page_type='home'):
    '''
        helper function to get script raw data
    '''
    try:
        page_url = get_url(route=route, page_type=page_type)
        response = requests.get(page_url)
        rawdata = bs(response.text, 'html.parser')
        return json.loads(rawdata.find_all('script', id = '__NEXT_DATA__')[0].text)
    except Exception as err:
        print('Some issue with Ineuron Website')
        raise err

def get_category_data():
    '''
        helper function to get category data
    '''
    data = get_script_data(route='', page_type='home')
    categories = data.get('props',{}).get('pageProps',{}).get('initialState',{}).get('init',{}).get('categories',{})
    categories_keys = categories.keys()
    category_data = []
    for num, category_key in enumerate(categories_keys):
        category_name = categories.get(category_key,{})['title']
        new_data = {
            'category-number' : num+1,
            'category-id' : category_key,
            'category-title' : category_name,
            'category-url' : get_url(route=category_name, page_type='category'),
            'course-subcategory' : []
        }
        sub_categories = categories.get(category_key,{}).get('subCategories',{})
        for sub_category in sub_categories.values():
            subcategory = {
                'subcategory-id' : sub_category.get('id'),
                'subcategory-title' : sub_category.get('title'),
                'subcategory-url' : get_url(route=sub_category.get('title'), page_type='category'),
            }
            new_data['course-subcategory'].append(subcategory)
        category_data.append(new_data)
    return category_data

def get_all_courses():
    rawdata = get_script_data(route='', page_type='home')
    json_data = rawdata.get('props',{}).get('pageProps',{}).get('initialState',{}).get('init',{}).get('courses',{})
    return json_data.keys()

def get_course_detailed_data(selected_course_name):
    '''
        helper function to get courses details
    '''
    # if(selected_course_name == ''):
    #     rawdata = get_script_data(route='', page_type='home')
    #     json_data = rawdata.get('props',{}).get('pageProps',{}).get('initialState',{}).get('init',{}).get('courses',{})
    # else:
    rawdata = get_script_data(route=selected_course_name, page_type='course')
    json_data = rawdata.get('props',{}).get('pageProps',{}).get('initialState',{}).get('init',{}).get('courses',{})
    # json_data = {selected_course_name.replace('-',' ') : json_data}
    course_details = json_data.get(selected_course_name,{})
    course = selected_course_name
    # courseData = []

    # bundles_count = {}
    # bundle_count_by_category = {}
    # for course, course_details in json_data.items():
    course_id = course_details['_id']
    description = course_details.get('description','')
    mode = course_details.get('mode','')
    category_id = course_details.get('categoryId', '')
    bundle_name = 'NA'
    if('courseInOneNeuron' in course_details):
        bundle_name = course_details['courseInOneNeuron']['bundleName']
    # if(bundle_name in bundles_count):
    #     bundles_count[bundle_name] = bundles_count[bundle_name] + 1
    # else:
    #     bundles_count[bundle_name] = 1
    # if(category_id in bundle_count_by_category):
    #     if(bundle_name in bundle_count_by_category[category_id]):
    #         bundle_count_by_category[category_id][bundle_name] = bundle_count_by_category[category_id][bundle_name] + 1
    #     else:
    #         bundle_count_by_category[category_id][bundle_name] = 1
    # else:
    #     bundle_count_by_category[category_id] = {}
    #     bundle_count_by_category[category_id][bundle_name] = 1
    inr_price = 'NA'
    usd_price = 'NA'
    if 'pricing' in course_details:
        if course_details['pricing']['isFree']:
            inr_price = 'Free'
            usd_price = 'Free'
        else:
            inr_price = course_details['pricing']['IN']
            usd_price = course_details['pricing']['US']
        
    instructorsDetails = course_details.get('instructorsDetails',[])
    for meta in course_details.get('courseMeta',[]):
        learn = meta.get('overview',{}).get('learn',[])
        requirements = meta.get('overview',{}).get('requirements',[])
        features = meta.get('overview',{}).get('features',[])
        language = meta.get('overview',{}).get('language',[])

    duration = ''
    curriculum = []
    if('data' in rawdata.get('props',{}).get('pageProps',{})):
        data = rawdata.get('props',{}).get('pageProps',{}).get('data')
        duration = data.get('meta',{}).get('duration','')
        for cur in data.get('meta',{}).get('curriculum',{}).values():
            new_cur = {
                'curriculum-title' : cur['title'],
                'curriculum-items' : []
            }
            for item in cur['items']:
                new_cur['curriculum-items'].append(item['title'])
            curriculum.append(new_cur)
    
    new_course_entry = {
        'course-id' : course_id,
        'course-name' : course,
        'course-description' : description,
        'course-mode' : mode,
        'course-language' : language,
        'course-duration' : duration,
        'course-learn' : learn,
        'course-requirements' : requirements,
        'course-features' : features,
        'course-inr-price' : inr_price,
        'course-usd-price' : usd_price,
        'course-curriculum' : curriculum,
        'course-instructor-details' : instructorsDetails,
        'course-category-id' : category_id,
        'course-bundle-name' : bundle_name
    }
    # courseData.append(new_course_entry)
    # return {
    #     'course-data' : courseData,
    #     'course-bundle-count' : bundles_count,
    #     'course-bundle-count-by-category' : bundle_count_by_category
    # }
    return new_course_entry

def get_course_details_data():
    # rawdata = get_script_data(route=selected_course_name, page_type='course')
    # json_data = rawdata.get('props',{}).get('pageProps',{}).get('initialState',{}).get('init',{}).get('courses',{}).get(selected_course_name.replace('-',' '),{})
    # duration = ''
    # curriculum = []
    # if('data' in rawdata.get('props',{}).get('pageProps',{})):
    #     data = rawdata.get('props',{}).get('pageProps',{}).get('data')
    #     duration = data.get('meta',{}).get('duration','')
    #     for cur in data.get('meta',{}).get('curriculum',{}).values():
    #         new_cur = {
    #             'curriculum-title' : cur['title'],
    #             'curriculum-items' : []
    #         }
    #         for item in cur['items']:
    #             new_cur['curriculum-items'].append(item['title'])
    #         curriculum.append(new_cur)    
    rawdata = get_script_data(route='', page_type='home')
    json_data = rawdata.get('props',{}).get('pageProps',{}).get('initialState',{}).get('init',{}).get('courses',{})
    
    coursesData = []
    bundles_count = {}
    bundle_count_by_category = {}
    for course in json_data.keys():
        course_data = get_course_detailed_data(course)
        coursesData.append(course_data)
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

    return {
        'course-data' : coursesData,
        'course-bundle-count' : bundles_count,
        'course-bundle-count-by-category' : bundle_count_by_category
    }

def insert_data_for_courses(course_data, mongodb):
    mongodb = mongodb.db
    if(mongodb[os.environ.get('MONGO_DB_COLL_COURSE')].count_documents({'_id' : course_data['course-name'].replace(' ','-')})):
        mongodb[os.environ.get('MONGO_DB_COLL_COURSE')].update_one(
            {'_id' : course_data['course-name'].replace(' ','-')},
            {'$set' : {'course-data' : course_data}}
        )
    else:
        mongodb[os.environ.get('MONGO_DB_COLL_COURSE')].insert_one({
            '_id' : course_data['course-name'].replace(' ','-'),
            'course-data' : course_data
        })

def insert_data_for_categories(category_data, mongodb):
    mongodb = mongodb.db
    if(mongodb[os.environ.get('MONGO_DB_COLL_CATEGORY')].count_documents({'_id' : category_data['category-id']})):
        mongodb[os.environ.get('MONGO_DB_COLL_CATEGORY')].update_one(
            {'_id' : category_data['category-id']},
            {'$set' : {'category-data' : category_data}}
        )
    else:
        mongodb[os.environ.get('MONGO_DB_COLL_CATEGORY')].insert_one({
            '_id' : category_data['category-id'],
            'category-data' : category_data
        })

def insert_course_bundle_count_by_category(bundle_count_by_category_key, bundle_count_by_category_value, mongodb):
    mongodb = mongodb.db
    if(mongodb[os.environ.get('MONGO_DB_COLL_COURSE_BNDL_CNT_CATGRY')].count_documents({'_id': bundle_count_by_category_key})):
        mongodb[os.environ.get('MONGO_DB_COLL_COURSE_BNDL_CNT_CATGRY')].update_one(
            {'_id' : bundle_count_by_category_key},
            {'$set' : {'category-bundle-count' : bundle_count_by_category_value}}
        )
    else:
        mongodb[os.environ.get('MONGO_DB_COLL_COURSE_BNDL_CNT_CATGRY')].insert_one({
            '_id' : bundle_count_by_category_key,
            'category-bundle-count' : bundle_count_by_category_value
        })

def insert_course_bundle_count(bundle_count_key, bundle_count_value, mongodb):
    mongodb = mongodb.db
    if(mongodb[os.environ.get('MONGO_DB_COLL_COURSE_BNDL_CNT')].count_documents({'_id': bundle_count_key})):
        mongodb[os.environ.get('MONGO_DB_COLL_COURSE_BNDL_CNT')].update_one(
            {'_id' : bundle_count_key},
            {'$set' : {'category-bundle-count' : bundle_count_value}}
        )
    else:
        mongodb[os.environ.get('MONGO_DB_COLL_COURSE_BNDL_CNT')].insert_one({
            '_id' : bundle_count_key,
            'category-bundle-count' : bundle_count_value
        })

def insert_course_description_data(course_data, mysqldb):
    data = ScrappedCourseData(
        course_id = course_data['course-id'],
        course_name = course_data['course-name'],
        course_description = course_data['course-description'],
        course_bundle_name = course_data['course-bundle-name'],
        course_language = course_data['course-language'],
        course_mode = course_data['course-mode'],
        category_id = course_data['course-category-id']
    )
    exists = mysqldb.session.query(mysqldb.exists().where(ScrappedCourseData.course_id == course_data['course-id'])).scalar()
    if(exists):
        existingdata = ScrappedCourseData.query.filter_by(course_id = course_data['course-id'])
        existingdata.course_name = course_data['course-name'],
        existingdata.course_description = course_data['course-description'],
        existingdata.course_bundle_name = course_data['course-bundle-name'],
        existingdata.course_language = course_data['course-language'],
        existingdata.course_mode = course_data['course-mode']
        existingdata.category_id = course_data['course-category-id']
    else:
        mysqldb.session.add(data)
    mysqldb.session.commit()

def generateCoursePdf(data: dict, savePdf=False):
    class PDF(FPDF):
        def __init__(self):
            super().__init__()
        def header(self):
            self.set_font('Arial', '', 12)
            # if(not os.path.exists('./logo.png')):
            #     url = r'https://ineuron.ai/images/ineuron-logo.png'
            #     img = open('logo.png', 'wb')
            #     img.write(requests.get(url).content)
            self.image('apps/static/images/ineuron-logo.png', w=40, h=20, type='PNG',x=210/2-20)
            self.cell(w=0,border=True)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', '', 9)
            self.cell(w=0,border=True)
            self.cell(0, 8, f'Page {self.page_no()}', 0, 0, 'C')

    def formatText(txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')

    # cell height
    ch = 6
    pdf = PDF()
    pdf.add_page()
    pdf.ln(4)
    pdf.set_font('Arial', 'BU', 16)
    pdf.multi_cell(w=0, h=5, txt=formatText(data.get('course-name','')), align='C')
    pdf.ln(4)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(w=0, h=5, txt=formatText(data.get('course-description','')))
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(w=210/3, h=ch, txt=f"Mode: {formatText(data.get('course-mode'))}", ln=0)
    pdf.cell(w=210/3, h=ch, txt=f"Language: {formatText(data.get('course-language',''))}", ln=0)
    pdf.cell(w=210/3, h=ch, txt=f"Duration: {formatText(data.get('course-duration',''))}", ln=1)

    # y_pos = 65

    # pdf.set_y(y_pos)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(w=30, h=ch, txt="What you'll learn:", ln=1)
    pdf.set_font('Arial', '', 9)
    for d in data.get('course-learn',[]):
        pdf.cell(w=30, h=ch, txt=f'{" "*4}{formatText(d)}', ln=1)
    pdf.ln(2)

    # pdf.set_xy(210/3, y_pos)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(w=30, h=ch, txt="Course Features:", ln=1)
    pdf.set_font('Arial', '', 9)
    for feature in data.get('course-features',[]):
        # pdf.set_x(210/3)
        pdf.cell(w=30, h=ch, txt=f'{" "*4}{formatText(feature)}', ln=1)
    pdf.ln(2)

    # pdf.set_xy(210*2/3,y_pos)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(w=30, h=ch, txt="Requirements:", ln=1)
    pdf.set_font('Arial', '', 9)
    for d in data.get('course-requirements',[]):
        # pdf.set_x(210*2/3)
        pdf.cell(w=30, h=ch, txt=f'{" "*4}{formatText(d)}', ln=1)
    pdf.ln(2)

    # pdf.set_x(210*2/3)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(w=30, h=ch, txt="Pricing:", ln=1)
    pdf.set_font('Arial', '', 9)
    # pdf.set_x(210*2/3)
    pdf.cell(w=0, h=ch, txt=f"{' '*4}{formatText(data.get('course-inr-price',''))} INR", ln=1)
    # pdf.set_x(210*2/3)
    pdf.cell(w=0, h=ch, txt=f"{' '*4}{formatText(data.get('course-usd-price',''))} USD", ln=1)
    pdf.ln(2)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(w=30, h=ch, txt="Course Curriculum:", ln=1)
    pdf.set_font('Arial', '', 9)
    for num, d in enumerate(data.get('course-curriculum',[])):
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(w=0, h=ch, txt='{}{}. {}'.format(" "*4,num+1, formatText(d.get('curriculum-title',''))), ln=1)
        for item in d['curriculum-items']:
            pdf.set_font('Arial', '', 9)
            pdf.cell(w=0, h=ch, txt=f"{' '*12}{formatText(item)}", ln=1)
    pdf.ln(2)

    pdf.set_font('Arial', 'B', 10)
    pdf.cell(w=30, h=ch, txt="Instructors:", ln=1)
    for num, d in enumerate(data.get('course-instructor-details',[])):
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(w=0, h=ch, txt='{}. {}'.format(num+1, formatText(d.get('name','').title())), ln=1)
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(w=0, h=5, txt=formatText(d.get('description','')))
        pdf.set_font('Arial', '', 9)
        pdf.cell(w=30, h=ch, txt=f"{' '*8}Email: ", ln=0)
        pdf.cell(w=100, h=ch, txt=formatText(d.get('email','')), ln=1)
        for key, value in d.get('social',{}).items():
            pdf.cell(w=30, h=ch, txt=f"{' '*8}{formatText(key)}: ", ln=0)
            pdf.cell(w=100, h=ch, txt=formatText(value), ln=1)
    # pdf.ln(4)
    if(savePdf):
        if(not os.path.exists('./pdfs')):
            os.mkdir('./pdfs')
        pdf.output(f'./pdfs/{data.get("course-name","testpdf").replace(" ","-")}.pdf', 'F')
        return f'Pdf has been saved at ./pdfs/{data.get("title","testpdf").replace(" ","-")}.pdf'
    else:
        return pdf.output(f'{data.get("course-name","testpdf").replace(" ","-")}.pdf', 'S').encode('latin-1')

def uploadToS3(fileName = '', pdfString = '', isSavedPdf = False):
    s3 = boto3.resource(
                service_name = 's3',
                region_name = os.environ.get('AWS_S3_REGION_NAME'),
                aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
    bucketName = os.environ.get('AWS_S3_BUCKET_NAME')
    if(isSavedPdf):
        if(os.path.exists(fileName)):
            s3.Bucket(bucketName).upload_file(Filename = fileName, Key = os.path.basename(fileName))
            print(os.path.basename(fileName), 'uploaded')
        else:
            print('No such file exists')
    else:
        s3.Bucket(bucketName).put_object(Key = f'{fileName.replace(" ","-")}.pdf', Body = pdfString)