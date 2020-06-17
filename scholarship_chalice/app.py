from chalice import Chalice
import pymysql
import sys
from configparser import ConfigParser  

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


@app.route('/addStudent', methods=['POST'])
def add_student(event):
    """
    This function fetches content from mysql RDS instance
    """
    result = []
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute("""select * from tbl_students WHERE StudentID = '%s'""" % (event['studentId']))
        result = cur.fetchone()
        if (result == None):
            cur.execute("""insert into tbl_students (StudentID, FirstName, LastName) 
            values( '%s', '%s', '%s')""" 
            % ( event['studentId'], event['firstName'], event['lastName']))
            conn.commit()
            for row in cur:
                print(row)
            cur.close()
            print('here')
            return {
                'statusCode' : 200,
            }
        else:
            cur.close()
            print('here2')
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
