import MySQLdb

database = MySQLdb.connect (host="127.0.0.1", user="root", passwd="", db = "UJ_RobotsDB")

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS Users")

sql = """CREATE TABLE UJ_RobotsDB. Users (
   USER_ID INT NOT NULL,
   USERNAME VARCHAR(255) NOT NULL,
   PASSWORD VARCHAR(255) NOT NULL,
   PRIMARY KEY (USER_ID)
)"""
cursor.execute(sql)

sql = """INSERT INTO Users(USER_ID, USERNAME, PASSWORD)
   VALUES(1, 'test', 'test_pass')"""

cursor.execute(sql)

query = "SELECT * FROM Users"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close()

print("Database version : %s " % data)
print("UJ Meta-Catalysis Data Inserted Successfully On The UJ Robots Production Database!!!")