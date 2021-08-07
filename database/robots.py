import MySQLdb
from connect import db_connect

database = db_connect()

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS Robots")

sql = """CREATE TABLE UJ_RobotsDB. Robots (
   ROBOT_ID VARCHAR(255) NOT NULL,
   ROBOT_KEY VARCHAR(255) NOT NULL,
   ROBOT_NAME VARCHAR(255) NOT NULL,
   IP_ADDRESS VARCHAR(255) NOT NULL,
   ROBOT_STATUS VARCHAR(255) NOT NULL,
   CURRENT_JOB VARCHAR(255) NOT NULL,
   ACTION BOOLEAN NOT NULL,
   LAST_UPDATE_DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   PRIMARY KEY (ROBOT_ID)
)"""
cursor.execute(sql)

sql = """INSERT INTO Robots(ROBOT_ID, ROBOT_KEY,  ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB, ACTION)
   VALUES('UJFB1', '#####', 'UJ Fluidic Backbone 1', '192.168.150', 'BUSY', 'Aspirin Synthesis', 1);
   INSERT INTO Robots(ROBOT_ID, ROBOT_KEY,  ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB, ACTION)
   VALUES('UJFB2', '#####', 'UJ Fluidic Backbone 2', '192.168.151', 'ERROR', 'Aspirin Synthesis', 1);
   INSERT INTO Robots(ROBOT_ID, ROBOT_KEY,  ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB, ACTION)
   VALUES('UJFB3','#####', 'UJ Fluidic Backbone 3', '192.168.152', 'OK', 'Aspirin Synthesis', 0);
   INSERT INTO Robots(ROBOT_ID, ROBOT_KEY,  ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB, ACTION)
   VALUES('UJFB4', '#####', 'UJ Fluidic Backbone 4', '192.168.153', 'BUSY', 'None', 0);
   INSERT INTO Robots(ROBOT_ID, ROBOT_KEY,  ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB, ACTION)
   VALUES('UJFB5', '#####', 'UJ Fluidic Backbone 5', '192.168.154', 'ERROR', 'None', 0);
   INSERT INTO Robots(ROBOT_ID, ROBOT_KEY,  ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB, ACTION)
   VALUES('UJFB6', '#####', 'UJ Fluidic Backbone 6', '192.168.155', 'OK', 'None', 1)"""

cursor.execute(sql)

query = "SELECT * FROM Robots"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close

print("Database version : %s " % data)
print("UJ Meta-Catalysis Data Inserted Successfully On The UJ Robots Production Database!!!")
