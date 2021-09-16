import MySQLdb
from connect import db_connect
from werkzeug.security import generate_password_hash

database = db_connect()

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS Robots")

sql = """CREATE TABLE UJ_RobotsDB. Robots (
   ROBOT_ID VARCHAR(255) NOT NULL,
   ROBOT_KEY VARCHAR(255) NOT NULL,
   ROBOT_NAME VARCHAR(255) NOT NULL,
   IP_ADDRESS VARCHAR(255) DEFAULT "",
   ROBOT_STATUS VARCHAR(255) DEFAULT "IDLE",
   CURRENT_JOB VARCHAR(255) DEFAULT "None",
   EXECUTE INT DEFAULT 1,
   ERROR_STATE INT DEFAULT 0, 
   LAST_UPDATE_DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   PRIMARY KEY (ROBOT_ID)
)"""
cursor.execute(sql)

raw_key = input("Please enter the secret key for the robot")
key = generate_password_hash(raw_key, method='sha256')

#sql = f"""INSERT INTO Robots(ROBOT_ID, ROBOT_KEY,  ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB, EXECUTE)
#    VALUES('UJFB1', '{key}', 'UJ Fluidic Backbone 1', '192.168.150', 'Idle', 'Idle', 0);
#   """

#cursor.execute(sql)

query = "SELECT * FROM Robots"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close()

print("Database version : %s " % data)
print("UJ Meta-Catalysis Data Inserted Successfully On The UJ Robots Production Database!!!")
