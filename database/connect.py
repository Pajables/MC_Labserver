import getpass
import MySQLdb


def db_connect():

    def user_details():
        username = input('Username:')
        password = getpass.getpass()
        return username, password

    print("please enter your credentials for the database")
    username, password = user_details()
    while True:
        try:
            database = MySQLdb.connect(host="127.0.0.1", user=username, passwd=password, db="UJ_RobotsDB")
            break
        except MySQLdb._exceptions.OperationalError:
            username, password = user_details()

    return database
