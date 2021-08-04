import MySQLdb

database = MySQLdb.connect(host="127.0.0.1", user="root", passwd="MySQL@DBA1993", db="UJ_RobotsDB")

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS Reactions")

sql = """CREATE TABLE UJ_RobotsDB. Reactions (
   REACTION_NAME VARCHAR(255) NOT NULL,
   TABLE_NAME VARCHAR(255) NOT NULL,
   LAST_UPDATE_DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)"""
cursor.execute(sql)

sql = """INSERT INTO Reactions(REACTION_NAME, TABLE_NAME)
   VALUES('Aspirin Synthesis', 'Robot_Status')"""

cursor.execute(sql)

query = "SELECT * FROM Reactions"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close

print("Database version : %s " % data)
print("UJ Meta-Catalysis Data Inserted Successfully On The UJ Robots Production Database!!!")