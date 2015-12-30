# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import MySQLdb
import urllib2
# import requests
from html2text import html2text
from urlparse import urljoin
from bs4 import BeautifulSoup

def send_mail():
    """发送邮件功能，未完成"""
    pass

def init_database():
    """初始化数据库"""
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
        url VARCHAR(100),
        title VARCHAR(100),
        content TEXT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(id));
    ''')

    cur.close()
    conn.close()

def read_html(url):
    """读取url的html源码"""
    req = urllib2.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0')
    handler = urllib2.urlopen(req)
    html = handler.read()
    return html

# def read_html(url):
#     # proxies = {'http':'http://127.0.0.1:3213'}
#     r = requests.get(url, proxies=proxies)
#     html = r.text
#     return html

def get_links(url):
    """get all chapter links from a gitbook url
    
    Args:
        url (str): a gitbook url

    Returns:
        list
    """
    soup = BeautifulSoup(read_html(url))
    tags = soup.find_all('li',class_='chapter')
    # use urljoin to convert relative path to absolute path
    links = [urljoin(url, tag.a.attrs['href']) 
             for tag in tags]
    
    return links 

def get_gitbook_chapter_data(url):
    """获取url对应gitbook章节的title和content

    Returns:
        Dict: 键为title和content
    """
    soup = BeautifulSoup(read_html(url))

    # get title
    title = soup.head.title.get_text().encode('utf-8')
    title = title.split('|')[0] # get rid of redundant info after |
    
    # get content
    contents_list = soup.find('section', id='section-').contents
    # convert unicode to String
    contents_html = ''.join([content.encode('utf-8')
                            for content in contents_list])
    contents_md = html2text(contents_html).encode('utf-8') # convert to markdown
    
    mydict = {'title': title, 'content': contents_md}
    return mydict


def is_title_in_Chapter_db(title, cur):
    """检查数据库里是否已经有这个gitbook title"""
    is_in = cur.execute(
               '''SELECT * FROM Chapter WHERE title=%s''',
               (title,))
    return is_in

def check_gitbook(url):
    """主流程:获取图书的所有章节链接，然后依次检查是否更新"""
    conn = MySQLdb.connect(
        host='127.0.0.1',unix_socket='/tmp/mysql.sock',
        user="root",passwd="",db="mipetest",charset='utf8')
    cur = conn.cursor()

    updated = False
    links = get_links(url)
    for link in links:
        print link
        chapter_data = get_gitbook_chapter_data(link)
        # print chapter_data['content']
        if not is_title_in_Chapter_db(chapter_data['title'], cur):
            cur.execute(
                '''INSERT INTO Chapter (title, content, url) VALUES (%s, %s, %s)''',
                (chapter_data['title'], chapter_data['content'], link))
            cur.connection.commit()
        else:
            cur.execute(
                'SELECT content FROM Chapter WHERE title=%s',
                (chapter_data['title'], ) )
            chapter_content_db = cur.fetchone()[0].encode('utf-8')
            if not chapter_content_db == chapter_data['content']:
                updated = True
                cur.execute(
                    '''UPDATE Chapter SET content=%s WHERE title=%s''',
                    (chapter_data['content'], chapter_data['title']))
                cur.connection.commit()
    if updated:
        send_mail() #TODO: 补全收件人参数
     

    cur.close()
    conn.close()

if __name__ == '__main__':
    url = "http://localhost:4000/"
    url = "https://wp-lai.gitbooks.io/learn-python/content/"
    check_gitbook(url)

    

   