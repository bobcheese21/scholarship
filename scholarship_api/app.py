from chalice import Chalice, AuthResponse
from chalicelib import parseUWTranscript
import pymysql
import sys
import base64
from configparser import ConfigParser  
import PyPDF2 as ppy

import json
from six.moves.urllib.request import urlopen
from functools import wraps
from jose import jwt

app = Chalice(app_name='scholarship_api')

config = ConfigParser()  
config.read('./chalicelib/config.ini')  

# get rds creds from config
REGION = config.get('rds', 'region')
rds_host  = config.get('rds', 'host')
name = config.get('rds', 'username')
password = config.get('rds', 'password')
db_name = config.get('rds', 'db_name')

AUTH0_DOMAIN = 'house37.us.auth0.com'
API_AUDIENCE = 'Sdte6FDTS7v3ay20iYooW8pdmu0VI8gu'
ALGORITHMS = ["RS256"]

@app.authorizer()
def jwt_auth(auth_request):
    token = auth_request.token
    jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://"+AUTH0_DOMAIN+"/"
            )
        except jwt.ExpiredSignatureError:
            print('tits1')
            return AuthResponse(routes=[], principal_id='user')
            # raise AuthError({"code": "token_expired",
            #                 "description": "token is expired"}, 401)
        except jwt.JWTClaimsError:
            print('tits2')
            return AuthResponse(routes=[], principal_id='user')
            # raise AuthError({"code": "invalid_claims",
            #                 "description":
            #                     "incorrect claims,"
            #                     "please check the audience and issuer"}, 401)
        except Exception:
            print('tits3')
            return AuthResponse(routes=[], principal_id='user')
            # raise AuthError({"code": "invalid_header",
            #                 "description":
            #                     "Unable to parse authentication"
            #                     " token."}, 401)

    return AuthResponse(routes=['/'], principal_id='user', context={'decodedJwt': payload})
    # raise AuthError({"code": "invalid_header",
    #                 "description": "Unable to find appropriate key"}, 401)


@app.route('/', authorizer=jwt_auth)
def index():
    print(app.current_request.context)
    print(app.current_request.context['authorizer']['decodedJwt'])
    return {'hello': 'world'}


@app.route('/createStudent', methods=['POST'], authorizer=jwt_auth)
def create_student():
    # get the decoded jwt
    user_info = app.current_request.context['authorizer']['decodedJwt']

    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute("""select * from tbl_students WHERE email = '%s'""" % (user_info['email']))
        result = cur.fetchone()

        # if the user does not exist create them
        if (result == None):
            cur.execute("""insert into tbl_students (email, firstName, lastName) 
            values( '%s', '%s', '%s')""" 
            % (user_info['email'], user_info['given_name'], user_info['family_name']))
            conn.commit()
            cur.close()
            return {
                'statusCode' : 200,
            }
        else:
            # user exists breh
            cur.close()
            return {
                'statusCode' : 400,
                'error' : 'Student Already Exists'
            }


@app.route('/createGroup', methods=['POST'], authorizer=jwt_auth)
def create_group():
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


@app.route('/joinGroup', methods=['POST'], authorizer=jwt_auth)
def join_group():
    # get decoded jwt
    user_info = app.current_request.context['authorizer']['decodedJwt']

    # get the body params
    body = app.current_request.json_body
    groupID = body['groupID']

    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute(""" select studentID from tbl_students where email = %s """ %
        (user_info['email']))

        # check the user exists
        if cur.rowcount == 0:
            cur.close()
            return {
                'statusCode' : 400,
                'error' : 'Student Does Not Exist'
            }

        # get the studentId
        studentID = cur.fetchone['studentId']

        # insert the student group relation
        cur.execute("""insert into tbl_groupsStud (studentID, groupID) 
        values( '%s', '%s')""" 
        % (studentID, body['groupID']))

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


@app.route('/uploadTranscript', methods=['POST'], authorizer=jwt_auth)
def upload_transcript():
    # get decoded jwt
    user_info = app.current_request.context['authorizer']['decodedJwt']

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
        parseUWTranscript.commitData(classes, body['userID'])
        # convert classes to the database
        return {
            'statusCode' : 200
        }
    return {
        'statusCode' : 400,
        'error' : 'Student Already Exists'
    }


@app.route('/login', methods=['GET'], authorizer=jwt_auth)
def login():
    # get decoded jwt
    user_info = app.current_request.context['authorizer']['decodedJwt']

    # check if the user exists and if they uploaded a transcript
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute(""" select studentID from tbl_students where email = %s """ 
        % (user_info['email']))

        # user does not exist
        if cursor.rowcount == 0:
            cur.close()
            return {
                'statusCode' : 200,
                'studentID' : -1
            }

        # get studentId of existing user
        result_set = cursor.fetchall()
        studentID = result_set[0]['studentID']
        cur.close()

        return {
            'statusCode' : 200,
            'studentID' : studentID
        }