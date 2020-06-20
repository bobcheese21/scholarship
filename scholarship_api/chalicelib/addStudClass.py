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
# #         cur.execute("""select * from tbl_students WHERE StudentID = '%s'""" % (event['StudentID']))
# #         result = cur.fetchone()
#         classEvent = event['classEvent']
#         print(classEvent)
#         cur.execute("""insert into tbl_studClass (StudentID, Quarter, ClassID, Year) values( '%s', '%s', (Select ClassID from tbl_classes WHERE ClassNum = %s and Dept = '%s' and ClassDesc like '%s' ), '%s')""" % ( event['StudentID'], event['Quarter'], classEvent['ClassNum'], classEvent['Dept'], str('%' + classEvent['ClassDesc'] + '%'), classEvent['Year'] ))
#         cur.executemany("insert into tbl_studClass (StudentID, Quarter, ClassID, Year) values( %s, %s, (Select ClassID from tbl_classes WHERE ClassNum = %s and Dept = %s and ClassDesc like %s ), '%s')", )
#         conn.commit()
#         for row in cur:
#             print(row)
#         cur.close()

def save_events(events):
    """
    This function fetches content from mysql RDS instance
    """
    result = []
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    with conn.cursor() as cur:
#         cur.execute("""select * from tbl_students WHERE StudentID = '%s'""" % (event['StudentID']))
#         result = cur.fetchone()
        cur.executemany("insert ignore into tbl_studClass (StudentID, Quarter, ClassID, Year) values( %s, %s, (Select ClassID from tbl_classes WHERE ClassNum = %s and Dept = %s and ClassDesc like %s ), %s)", events)
        conn.commit()
        for row in cur:
            print(row)
        cur.close()
        
def main(events):
    save_events(events)