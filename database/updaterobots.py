import MySQLdb

database = MySQLdb.connect (host="127.0.0.1", user="root", passwd="", db="UJ_RobotsDB")

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

sql = """UPDATE robots
   SET ROBOT_ID = 'UJFB2'
   WHERE ROBOT_KEY = '########';
   
   COMMIT;
   """

cursor.execute(sql)

query = "SELECT * FROM Robots"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close()

print("Database version : %s " % data)
print("UJ Meta-Catalysis Robots Updated Successfully On The UJ Robots Production Database!!!")

