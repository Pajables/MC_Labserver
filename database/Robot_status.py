import MySQLdb

database = MySQLdb.connect (host="127.0.0.1", user = "root", passwd = "", db = "UJ_RobotsDB")

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS Robot_Status")

sql = """CREATE TABLE UJ_RobotsDB. Robot_Status (
   ROBOT_ID VARCHAR(255) NOT NULL,
   ROBOT_NAME VARCHAR(255) NOT NULL,
   IP_ADDRESS VARCHAR(255) NOT NULL,
   ROBOT_STATUS CHAR(10) NOT NULL,
   CURRENT_JOB VARCHAR(255) NOT NULL,
   LAST_UPDATE_DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   PRIMARY KEY (ROBOT_ID)
)"""
cursor.execute(sql)

sql = """INSERT INTO Robot_Status(ROBOT_ID, ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB)
   VALUES('UJFB1', 'UJ Fluidic Backbone 1', '192.168.150', 'BUSY', 'Aspirin Synthesis');
   INSERT INTO Robot_Status(ROBOT_ID, ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB)
   VALUES('UJFB2', 'UJ Fluidic Backbone 2', '192.168.151', 'ERROR', 'Aspirin Synthesis');
   INSERT INTO Robot_Status(ROBOT_ID, ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB)
   VALUES('UJFB3', 'UJ Fluidic Backbone 3', '192.168.152', 'OK', 'Aspirin Synthesis');
   INSERT INTO Robot_Status(ROBOT_ID, ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB)
   VALUES('UJFB4', 'UJ Fluidic Backbone 4', '192.168.153', 'BUSY', 'None');
   INSERT INTO Robot_Status(ROBOT_ID, ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB)
   VALUES('UJFB5', 'UJ Fluidic Backbone 5', '192.168.154', 'ERROR', 'None');
   INSERT INTO Robot_Status(ROBOT_ID, ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB)
   VALUES('UJFB6', 'UJ Fluidic Backbone 6', '192.168.155', 'OK', 'None')"""

cursor.execute(sql)

query = "SELECT * FROM Robot_Status"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close

print("Database version : %s " % data)
print("UJ Meta-Catalysis Data Inserted Successfully On The UJ Robots Production Database!!!")
