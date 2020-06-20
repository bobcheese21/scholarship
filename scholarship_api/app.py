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
def demo_auth(auth_request):
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

        print(payload)
    return AuthResponse(routes=['/'], principal_id='user')
    # raise AuthError({"code": "invalid_header",
    #                 "description": "Unable to find appropriate key"}, 401)


@app.route('/', authorizer=demo_auth)
def index():
    print(app.current_request.context)
    return {'hello': 'world'}




# Format error response and append status code
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
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
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated



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
        parseUWTranscript.commitData(classes, body['userID'])
        # convert classes to the database
        return {
            'statusCode' : 200
        }
    return {
        'statusCode' : 400,
        'error' : 'Student Already Exists'
    }


@app.route('/login/{jwt}', methods=['GET'])
def login(jwt):
    # decode the jwt 
    # check if the user exists and if they uploaded a transcript
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute(""" select studentID from tbl_students where email = %s """ 
        % (email))

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
