import MySQLdb
from connect import db_connect

database = db_connect()

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS Reactions")

sql = """CREATE TABLE UJ_RobotsDB. Reactions (
   REACTION_NAME VARCHAR(255) NOT NULL,
   TABLE_NAME VARCHAR(255) NOT NULL,
   FILE_NAME TEXT NOT NULL,
   PRIMARY KEY (REACTION_NAME)
)"""
cursor.execute(sql)

query = "SELECT * FROM Reactions"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close()

print("Database version : %s " % data)
print("UJ Meta-Catalysis Data Inserted Successfully On The UJ Robots Production Database!!!")
