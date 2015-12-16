import MySQLdb

def init_database():
    conn = MySQLdb.connect(host='127.0.0.1',unix_socket='/tmp/mysql.sock',
                           user="root",passwd="",db="mipetest",charset='utf8')
    cur = conn.cursor()

    # cur.execute("CREATE DATABASE mipetest;")
    # cur.execute("USE mipetest")

    cur.execute(
    '''
    CREATE TABLE User (
        id INT NOT NULL AUTO_INCREMENT,
        ghName VARCHAR(45),
        email VARCHAR(45),
        PRIMARY KEY(id));

    CREATE TABLE Author (
        id INT NOT NULL AUTO_INCREMENT,
        ghName VARCHAR(45),
        PRIMARY KEY(id));

    CREATE TABLE Subscribe (
        user_id INT NOT NULL,
        book_id INT NOT NULL,
        PRIMARY KEY(user_id, book_id));

    CREATE TABLE Book (
        id INT NOT NULL AUTO_INCREMENT,
        url VARCHAR(45),
        name VARCHAR(45),
        author_id INT,
        PRIMARY KEY(id));

    CREATE TABLE Chapter (
        id INT NOT NULL AUTO_INCREMENT,
        url VARCHAR(45),
        title VARCHAR(100),
        content VARCHAR(10000),
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(id))
    ''')

    cur.close()
    conn.close()

if __name__ == '__main__':
    init_database()