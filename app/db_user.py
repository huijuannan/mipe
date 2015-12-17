# -*- coding: utf-8 -*-
'''
User and subscription database operation.
'''

import MySQLdb as mdb
import sae.const

def db_conn():
    '''建立 SAE 共享型 mysql 的数据库连接'''
    host = sae.const.MYSQL_HOST
    port = int(sae.const.MYSQL_PORT)
    user = sae.const.MYSQL_USER
    passwd = sae.const.MYSQL_PASS
    db = sae.const.MYSQL_DB
    con = mdb.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset='utf8')
    return con

def insert_user(ghName, email):
    '''新增一行 user 数据，无 User 表时新建此表'''
    con = db_conn()
    with con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS User(
            id INTEGER PRIMARY KEY AUTO_INCREMENT, 
            ghName VARCHAR(45), 
            email VARCHAR(45))''')
        cur.execute("INSERT INTO User(ghName, email) VALUES(%s, %s)", 
            (ghName, email))

def get_user_by_id(id):
    '''根据 id 获取一行 user 数据，返回一个字典（无此 id 时返回 None）'''
    con = db_conn()
    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT * FROM User where id=%s", (id,))
        row = cur.fetchone()
    return row

def get_user_by_name(name):
    '''根据 ghName 获取一行 user 数据，返回一个字典（无此 name 时返回 None）'''
    con = db_conn()
    with con:
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT * FROM User where ghName=%s", (name,))
        row = cur.fetchone()
    return row

# 以下为 订阅数据处理部分，尚未完成
#def get_subs(user_id):
#    '''由当前用户的 id 获取其订阅的所有 gitbook 书名和 url
#    返回一个字典的元组，无订阅时返回空元组
#    '''
#    con = db_conn()
#    with con:
#        cur = con.cursor(mdb.cursors.DictCursor)
#        cur.execute('''CREATE TABLE IF NOT EXISTS Subscribe(
#            User.id INTEGER, 
#            Book.id INTEGER, 
#            PRIMARY KEY (User.id, Book.id)''')

#def add_sub(sub, user_id):
#    '''新增一行 subscribe 数据'''

#def del_sub(sub, user_id):