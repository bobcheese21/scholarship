from chalice import Chalice
import pymysql
import sys
from configparser import ConfigParser  
from parseUWTranscript import getClasses

config = ConfigParser()  
config.read('./config.ini')  

# get rds creds from config
REGION = config.get('rds', 'region')
rds_host  = config.get('rds', 'host')
name = config.get('rds', 'username')
password = config.get('rds', 'password')
db_name = config.get('rds', 'db_name')

app = Chalice(app_name='scholarship_chalice')


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/createStudent', methods=['POST'])
def create_student(event):
    """
    This function fetches content from mysql RDS instance
    """
    result = []
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute("""select * from tbl_students WHERE email = '%s'""" % (event['email']))
        result = cur.fetchone()
        if (result == None):
            cur.execute("""insert into tbl_students (email, firstName, lastName) 
            values( '%s', '%s', '%s')""" 
            % (event['email'], event['firstName'], event['lastName']))
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
def create_group(event):
    result = []
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute("""insert into tbl_groups (name, description) 
        values( '%s', '%s', '%s')""" 
        % (event['name'], event['description']))
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
def join_group(event):
    groupID = event['groupID']
    studentID = event['studentID']
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute("""insert into tbl_groupsStud (studentID, groupID) 
        values( '%s', '%s')""" 
        % (event['studentID'], event['groupID']))
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
def upload_transcript(event):
    # get the base64 encoded pdf
    pdf_base64 = event['transcriptData']
    with open("transcript.pdf", "wb") as transcript:
        # write the base64 to the file
        transcript.write(pdf_base64.decode('base64'))
        # parse the pdf
        pdf2 = ppy.PdfFileReader("transcript.pdf")
        print(getClasses(pdf2))

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
