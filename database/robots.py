import MySQLdb

database = MySQLdb.connect (host="127.0.0.1", user = "root", passwd = "Evildogs&Zombies12", db = "UJ_RobotsDB")

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS Robots")

sql = """CREATE TABLE UJ_RobotsDB. Robots (
   ROBOT_ID VARCHAR(255) NOT NULL,
   ROBOT_KEY VARCHAR(255) NOT NULL,
   LAST_UPDATE_DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   PRIMARY KEY (ROBOT_ID)
)"""
cursor.execute(sql)

sql = """INSERT INTO Robots(ROBOT_ID, ROBOT_KEY)
   VALUES('UJFB1', '########')"""

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
