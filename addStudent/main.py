import pymysql
import sys


REGION = 'us-west-2a'

rds_host  = "eatmyass.czvhjizhxvs4.us-west-2.rds.amazonaws.com"
name = "eatmyass"
password = "eatmyasspassword"
db_name = "eatmyass"


def save_events(event):
    """
    This function fetches content from mysql RDS instance
    """
    result = []
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
        cur.execute("""select * from tbl_students WHERE StudentID = '%s'""" % (event['StudentID']))
        result = cur.fetchone()
        if (result == None):
            cur.execute("""insert into tbl_students (StudentID, FirstName, LastName) values( '%s', '%s', '%s')""" % ( event['StudentID'], event['FirstName'], event['LastName']))
            conn.commit()
            for row in cur:
                print(row)
        else:
            print('Student Already Exists')
        cur.close()


def main(event):
    save_events(event)