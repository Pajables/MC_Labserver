import MySQLdb

database = MySQLdb.connect (host="127.0.0.1", user = "root", passwd = "", db = "UJ_RobotsDB")

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS Reaction_Status")

sql = """CREATE TABLE UJ_RobotsDB. Reaction_Status (
   REACTION_ID INT NOT NULL,
   ROBOT_ID VARCHAR(255) NOT NULL,
   ROBOT_NAME VARCHAR(255) NOT NULL,
   REACTION_NAME VARCHAR(255) NOT NULL,
   REACTION_STATUS CHAR(35) NOT NULL,
   LAST_UPDATE_DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   JOB_COMPLETION_DATE DATE,
   PRIMARY KEY (REACTION_ID)
)"""
cursor.execute(sql)

sql = """INSERT INTO Reaction_Status(REACTION_ID, ROBOT_ID, ROBOT_NAME, REACTION_NAME, REACTION_STATUS, JOB_COMPLETION_DATE)
   VALUES(0, 'UJFB1', 'UJ Fluidic Backbone 1', 'Aspirin Synthesis', 'In-Progress', NULL);
   INSERT INTO Reaction_Status(REACTION_ID, ROBOT_ID, ROBOT_NAME, REACTION_NAME, REACTION_STATUS, JOB_COMPLETION_DATE)
   VALUES(1, 'UJFB1', 'UJ Fluidic Backbone 1', 'Aspirin Synthesis', 'Complete', 20210709)"""

cursor.execute(sql)

query = "SELECT * FROM Reaction_Status"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close

print("Database version : %s " % data)
print("UJ Meta-Catalysis Data Inserted Successfully On The UJ Robots Production Database!!!")
