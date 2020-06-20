from chalice import Chalice
from chalicelib import parseUWTranscript
import pymysql
import sys
import base64
from configparser import ConfigParser  
import PyPDF2 as ppy

app = Chalice(app_name='scholarship_api')

config = ConfigParser()  
config.read('./chalicelib/config.ini')  

# get rds creds from config
REGION = config.get('rds', 'region')
rds_host  = config.get('rds', 'host')
name = config.get('rds', 'username')
password = config.get('rds', 'password')
db_name = config.get('rds', 'db_name')

@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/createStudent', methods=['POST'])
def create_student():
    body = app.current_request.json_body
    result = []
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute("""select * from tbl_students WHERE email = '%s'""" % (body['email']))
        result = cur.fetchone()
        if (result == None):
            cur.execute("""insert into tbl_students (email, firstName, lastName) 
            values( '%s', '%s', '%s')""" 
            % (body['email'], body['firstName'], body['lastName']))
            conn.commit()
            cur.close()
            return {
                'statusCode' : 200,
            }
        else:
            cur.close()
            return {
                'statusCode' : 400,
                'error' : 'Student Already Exists'
            }


@app.route('/createGroup', methods=['POST'])
def create_group():
    body = app.current_request.json_body
    result = []
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute("""insert into tbl_groups (name, description) 
        values( '%s', '%s', '%s')""" 
        % (body['name'], body['description']))
        conn.commit()

        cur.close()
        return {
            'statusCode' : 200
        }
    # not sure how with as statements work, my thought is that if the sql fails
    # it will come here and if it succeeds it will return before this
    return {
        'statusCode' : 400
    }


@app.route('/joinGroup', methods=['POST'])
def join_group():
    body = app.current_request.json_body
    groupID = body['groupID']
    studentID = body['studentID']
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute("""insert into tbl_groupsStud (studentID, groupID) 
        values( '%s', '%s')""" 
        % (body['studentID'], body['groupID']))
        conn.commit()

        cur.close()
        return {
            'statusCode' : 200
        }
    # not sure how with as statements work, my thought is that if the sql fails
    # it will come here and if it succeeds it will return before this
    return {
        'statusCode' : 400,
        'error' : 'Student Already Exists'
    }


@app.route('/uploadTranscript', methods=['POST'])
def upload_transcript():
    body = app.current_request.json_body
    # get the base64 encoded pdf
    pdf_base64 = body['transcriptData']
    with open("transcript.pdf", "wb") as transcript:
        # write the base64 to the file
        base64_message = pdf_base64
        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        transcript.write(message_bytes)
        # parse the pdf
        pdf2 = ppy.PdfFileReader("transcript.pdf")
        classes = parseUWTranscript.getClasses(pdf2)
        print(classes)
        # convert classes to the database
        return {
            'statusCode' : 200
        }
    return {
        'statusCode' : 400,
        'error' : 'Student Already Exists'
    }

# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
