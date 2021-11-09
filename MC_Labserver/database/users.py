import MySQLdb
from connect import db_connect, check_password
from werkzeug.security import generate_password_hash

database = db_connect()

cursor = database.cursor()

cursor.execute("SELECT VERSION()")

data = cursor.fetchone()

cursor.execute("DROP TABLE IF EXISTS Users")

print('Please set up an Admin user for the Flask webserver.',
      'This admin user will be able to add other admins to the server')

username = input("What is the Admin's username?")
password = generate_password_hash(check_password(), method='sha256')

sql = """CREATE TABLE UJ_RobotsDB. Users (
   USER_ID INT NOT NULL,
   USERNAME VARCHAR(255) NOT NULL,
   PASSWORD VARCHAR(255) NOT NULL,
   ADMIN INT NOT NULL,
   PRIMARY KEY (USER_ID)
)"""
cursor.execute(sql)

# User id 0 is reserved for the synthesis planner script

sql = f"""INSERT INTO Users(USER_ID, USERNAME, PASSWORD, ADMIN)
 VALUES(1, '{username}', '{password}', 1)
 """

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