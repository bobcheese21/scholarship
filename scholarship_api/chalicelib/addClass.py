import pymysql
import sys


REGION = 'us-west-2a'

rds_host  = "eatmyass.czvhjizhxvs4.us-west-2.rds.amazonaws.com"
name = "eatmyass"
password = "eatmyasspassword"
db_name = "eatmyass"


# def save_events(event):
#     """
#     This function fetches content from mysql RDS instance
#     """
#     result = []
#     conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
#     with conn.cursor() as cur:
#         cur.execute("""select * from tbl_classes WHERE Dept = '%s' and ClassNum = '%s'""" % (event['Dept'], event['ClassNum']))
#         result = cur.fetchone()
#         if (result == None):
#             cur.execute("""insert into tbl_classes (Dept, ClassNum, ClassDesc) values( '%s', '%s', '%s')""" % ( event['Dept'], event['ClassNum'], event['ClassDesc']))
#             conn.commit()
#             for row in cur:
#                 print(row)
#         else:
#             print('Class Already Exists')
#         cur.close()

def save_events(events):
    """
    This function fetches content from mysql RDS instance
    """
    result = []
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
#         cur.execute("""select * from tbl_classes WHERE Dept = '%s' and ClassNum = '%s'""" % (event['Dept'], event['ClassNum']))
#         result = cur.fetchone()
#         if (result == None):
#         cur.execute("""insert into tbl_classes (Dept, ClassNum, ClassDesc) values( '%s', '%s', '%s')""" % ( event['Dept'], event['ClassNum'], event['ClassDesc']))
        cur.executemany("insert ignore into tbl_classes (Dept, ClassNum, ClassDesc) values( %s, %s, %s)", events)
        conn.commit()
        for row in cur:
            print(row)
#         else:
#             print('Class Already Exists')
        cur.close()

def main(events):
    save_events(events)