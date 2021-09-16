import MySQLdb
from connect import db_connect

database = db_connect()

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS Reactions_Status")

sql = """CREATE TABLE UJ_RobotsDB. Reactions_Status (
   REACTION_ID INT,
   ROBOT_ID VARCHAR(255) NOT NULL,
   ROBOT_NAME VARCHAR(255) NOT NULL,
   REACTION_NAME VARCHAR(255) NOT NULL,
   REACTION_STATUS VARCHAR(255) NOT NULL,
   TABLE_NAME VARCHAR(255) NOT NULL,
   LAST_UPDATE_DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   JOB_COMPLETION_DATE DATE,
   PRIMARY KEY (REACTION_ID)
)"""
cursor.execute(sql)

# sql = """INSERT INTO Reactions_Status(REACTION_ID, ROBOT_ID, ROBOT_NAME, REACTION_NAME, REACTION_STATUS, TABLE_NAME, JOB_COMPLETION_DATE)
#    VALUES(0, 'UJFB1', 'UJ Fluidic Backbone 1', 'Aspirin Synthesis', 'In-Progress', 'ASPIRIN1', NULL);
#    INSERT INTO Reactions_Status(REACTION_ID, ROBOT_ID, ROBOT_NAME, REACTION_NAME, REACTION_STATUS, TABLE_NAME, JOB_COMPLETION_DATE)
#    VALUES(1, 'UJFB1', 'UJ Fluidic Backbone 1', 'Aspirin Synthesis', 'Complete', 'ASPIRIN1', 20210709)"""
#
# cursor.execute(sql)

query = "SELECT * FROM Reactions_Status"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close()

print("Database version : %s " % data)
print("UJ Meta-Catalysis Data Inserted Successfully On The UJ Robots Production Database!!!")
