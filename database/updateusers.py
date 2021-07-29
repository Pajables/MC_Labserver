import MySQLdb

database = MySQLdb.connect (host="127.0.0.1", user = "root", passwd = "", db = "UJ_RobotsDB")

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

sql = """UPDATE users
   SET USERNAME = 'Metacatalysis'
   WHERE PASSWORD = '########';
   
   Commit;
   """

cursor.execute(sql)

query = "SELECT * FROM Users"

cursor.execute(query)

records = cursor.fetchall()

for record in records:
    print(record)

cursor.close()

database.commit()

database.close

print("Database version : %s " % data)
print("UJ Meta-Catalysis Users Updated Successfully On The UJ Robots Production Database!!!")

