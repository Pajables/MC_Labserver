import MySQLdb

database = MySQLdb.connect (host="127.0.0.1", user = "root", passwd = "Evildogs&Zombies12", db = "UJ_RobotsDB")

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS UJ_Robots_Communication")

sql = """CREATE TABLE UJ_RobotsDB. UJ_Robots_Communication (
   ROBOT_ID VARCHAR(255) NOT NULL,
   ROBOT_NAME VARCHAR(255) NOT NULL,
   STATUS CHAR(10) NOT NULL, 
   EXECUTE INT NOT NULL,
   LAST_UPDATE_DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   PRIMARY KEY(ROBOT_ID)
)"""
cursor.execute(sql)

sql = """INSERT INTO UJ_Robots_Communication(ROBOT_ID, ROBOT_NAME, STATUS, EXECUTE)
   VALUES('UJFB1', 'UJ Fluidic Backbone 1', 'ERROR', 1);
   INSERT INTO UJ_Robots_Communication(ROBOT_ID, ROBOT_NAME, STATUS, EXECUTE)
   VALUES('UJFB2', 'UJ Fluidic Backbone 2', 'ERROR', 0);
   INSERT INTO UJ_Robots_Communication(ROBOT_ID, ROBOT_NAME, STATUS, EXECUTE)
   VALUES('UJFB3', 'UJ Fluidic Backbone 3', 'OK', 1);
   INSERT INTO UJ_Robots_Communication(ROBOT_ID, ROBOT_NAME, STATUS, EXECUTE)
   VALUES('UJFB4', 'UJ Fluidic Backbone 4', 'OK', 0)"""

cursor.execute(sql)

query = "SELECT * FROM UJ_Robots_Communication"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close

print("Database version : %s " % data)
print("UJ Meta-Catalysis Data Inserted Successfully On The UJ Robots Communication Production Database!!!")

