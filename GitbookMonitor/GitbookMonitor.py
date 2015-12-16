import MySQLdb
import urllib2
from urlparse import urljoin
from bs4 import BeautifulSoup

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

def get_links(url):
    """get all chapter links from a gitbook url
    
    Arg:
        url :

    Return:

    """
    req = urllib2.Request(url)
    handler = urllib2.urlopen(req)
    html = handler.read()

    soup = BeautifulSoup(html)
    tags = soup.find_all('li',class_='chapter')
    links = [urljoin(url, tag.a.attrs['href']) 
             for tag in tags]
    
    return links 

if __name__ == '__main__':
    url = "http://localhost:4000/"
    print get_links(url)
   