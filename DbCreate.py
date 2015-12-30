from __future__ import print_function
import mysql.connector 
from mysql.connector import errorcode

# set up config info
config = {
    'user' : ''
    'password' : ''
}

DB_NAME = 'mipe'

# store SQL create commands into TABLES
TABLES = {}

TABLES['user'] = (
    "CREATE TABLE User ("
    "id INT NOT NULL AUTO_INCREMENT,"
    "ghName VARCHAR(45),"
    "email VARCHAR(45),"
    "PRIMARY KEY(id))"
    "CHARACTER SET utf8 COLLATE utf8_general_ci;")

TABLES['author'] = (
    "CREATE TABLE Author ("
    "id INT NOT NULL AUTO_INCREMENT,"
    "name VARCHAR(45),"
    "PRIMARY KEY(id))"
    "CHARACTER SET utf8 COLLATE utf8_general_ci;")

TABLES['subscriber'] = (
    "CREATE TABLE Subscribe ("
    "user_id INT NOT NULL,"
    "book_id INT NOT NULL,"
    "PRIMARY KEY(user_id, book_id))" 
    "CHARACTER SET utf8 COLLATE utf8_general_ci;")

TABLES['book'] = (
    "CREATE TABLE Book ("
    "id INT NOT NULL AUTO_INCREMENT,"
    "url VARCHAR(45),"
    "name VARCHAR(45),"
    "author_id INT,"
    "PRIMARY KEY(id))"
    "CHARACTER SET utf8 COLLATE utf8_general_ci;")

TABLES['chapter'] = (
    "CREATE TABLE Chapter ("
    "id INT NOT NULL AUTO_INCREMENT,"
    "url VARCHAR(100),"
    "title VARCHAR(100),"
    "content TEXT,"
    "created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
    "book_id INT,"
    "PRIMARY KEY(id))"
    "CHARACTER SET utf8 COLLATE utf8_general_ci;")

def create_database(cursor):
    try:
        cursor.execute( "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME)) 
    except mysql.connector.Error as err: 
        print("Failed creating database: {}".format(err)) 
        exit(1)

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# if database DB_NAME doesn't exist, creat one
try:
    cnx.database = DB_NAME 
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor) 
        cnx.database = DB_NAME 
    else:
        print(err)
    exit(1)

for name, ddl in TABLES.iteritems():
    try:
        print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")


cursor.close()
cnx.close()
