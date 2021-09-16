import MySQLdb
from connect import db_connect

database = db_connect()

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS Robot_Queue")

sql = """CREATE TABLE UJ_RobotsDB. Robot_Queue (
   USER_ID INT NOT NULL,
   ROBOT_ID VARCHAR(255) NOT NULL,
   REACTION_NAME VARCHAR(255),
   REACTION_ID INT NOT NULL,
   QUEUE_NUM INT AUTO_INCREMENT,
   LAST_UPDATE_DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   PRIMARY KEY (QUEUE_NUM)
)"""
cursor.execute(sql)

# sql = """INSERT INTO Robot_Queue(ROBOT_ID, QUEUE_NUM, FILE_NAME)
#    VALUES('UJFB1', 0, '/home/MCLabserver/templates')"""
#
# cursor.execute(sql)

query = "SELECT * FROM Robot_Queue"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close()

print("Database version : %s " % data)
print("UJ Meta-Catalysis Data Inserted Successfully On The UJ Robots Production Database!!!")