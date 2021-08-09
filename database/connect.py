import getpass
import MySQLdb


def user_details():
    username = input('Username for database:')
    password = getpass.getpass()
    return username, password


def check_password():

    def enter_pass():
        print('Enter a password')
        attempt1 = getpass.getpass()
        print('Please confirm your password')
        attempt2 = getpass.getpass()
        return attempt1, attempt2

    password1, password2 = enter_pass()
    while password1 != password2:
        password1, password2 = enter_pass()

    return password1


def db_connect():
    print("please enter your credentials for the database")
    username, password = user_details()
    while True:
        try:
            database = MySQLdb.connect(host="127.0.0.1", user=username, passwd=password, db="UJ_RobotsDB")
            break
        except MySQLdb._exceptions.OperationalError:
            username, password = user_details()

    return database
