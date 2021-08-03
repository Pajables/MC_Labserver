import MySQLdb

database = MySQLdb.connect (host="127.0.0.1", user="root", passwd="", db = "UJ_RobotsDB")

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS Reaction_Parameters")

sql = """CREATE TABLE UJ_RobotsDB. Reaction_Parameters (
   REACTION_NAME VARCHAR(255) NOT NULL,
   ROBOT_ID VARCHAR(255) NOT NULL,
   ROBOT_NAME VARCHAR(255) NOT NULL,
   PARM1 VARCHAR(255) NOT NULL,
   PARM1_VALUE VARCHAR(255) NOT NULL,
   LAST_UPDATE_DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   PRIMARY KEY (REACTION_NAME)
)"""
cursor.execute(sql)

sql = """INSERT INTO Reaction_Parameters(REACTION_NAME, ROBOT_ID, ROBOT_NAME, PARM1, PARM1_VALUE)
   VALUES('Aspirin Synthesis', 'UJFB1', 'UJ Fluidic Backbone 1', 'Volume acetic anhydride', '10.0ml')"""

cursor.execute(sql)

query = "SELECT * FROM Reaction_Parameters"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close()

print("Database version : %s " % data)
print("UJ Meta-Catalysis Data Inserted Successfully On The UJ Robots Production Database!!!")
