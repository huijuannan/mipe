#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIPE - web app 

采用 flask 框架
"""
from urlparse import urlparse

from flask import (Flask, request, redirect, render_template,
        session, url_for, g, flash, abort)
from flask_dance.contrib.github import make_github_blueprint, github

import torndb # A lightweight wrapper around MySQLdb
import config

# configuration
SECRET_KEY = 'secretkey'

# create application
app = Flask(__name__)
app.debug = True
app.secret_key = SECRET_KEY
blueprint = make_github_blueprint(
    client_id=config.OAUTH_CLIENT_ID,
    client_secret=config.OAUTH_CLIENT_SECRET,
    scope=u'user:email',
)

app.register_blueprint(blueprint, url_prefix="/login")

@app.before_request
def before_request():
    '''在 request 之前：
    1、建立 MySQL 数据库连接
    2、检验用户登录状态，若已登录则存入 g.user
    '''
    
    # 建立 MySQL 连接，参数：host:port, database, user, passwd
    # torndb 默认已将 charset 设为 utf-8
    g.db = torndb.Connection(
        config.MYSQL_HOST,
        config.MYSQL_DB,
        config.MYSQL_USER,
        config.MYSQL_PW
        )
    
    g.user = None

    if github.authorized:
        gh_name = github.get("/user").json()['login']

        existing_user = g.db.get("SELECT * FROM User where ghName=%s", gh_name)

        if existing_user == None:
            email = github.get("/user").json()['email']
            g.db.insert("INSERT INTO User (ghName, email) VALUES (%s, %s)", 
                gh_name, email)

        g.user = g.db.get("SELECT * FROM User where ghName=%s", 
                        gh_name)
        
@app.after_request
def close_connection(response):
    '''request 结束后关闭数据库连接'''
    g.db.close()
    return response

@app.route('/')
def home():
    '''显示用户订阅条目
    未登录时重定向到登录页面
    '''
    if not github.authorized: 
        return redirect(url_for('login'))

    subs = g.db.query(
        '''SELECT book_id, url, name, ghName 
        FROM Subscribe, Book, Author
        WHERE Subscribe.book_id = Book.id
        AND Book.author_id = Author.id
        AND Subscribe.user_id = %s
        ''', g.user.id) 
    # subs 为字典构成的列表
    # 字典的键：'book_id', 'url', 'name'(书名), 'ghName'(作者的github用户名)
    
    for sub in subs:
        sub['rmlink'] = '/remove_sub/'+str(sub['book_id'])

    return render_template('home.html',subscriptions=subs)

@app.route('/add_sub', methods=['POST'])
def add_sub():
    '''为当前用户增加一个订阅，录入作者、书目、订阅信息'''

    if not github.authorized:
        abort(401)

    if request.form['new_sub']:
        url = request.form['new_sub']
        if len(url) > 100:
            flash(u'添加失败：url 地址过长！')
            #is_url_valid = False
            return redirect(url_for('home'))

        #url 有效性检查, 格式：https://authorname.gitbooks.io/bookname/content/
        url_scheme = urlparse(url).scheme # expected: 'https'
        url_hostname = urlparse(url).hostname # expected: 'authorname.gitbooks.io'
        url_path = urlparse(url).path # expected: '/bookname/content/'
        
        if url_scheme != 'https' or\
                url_hostname.partition('.')[2] != 'gitbooks.io' or\
                not url_path.endswith('/content/'):

            flash(u'添加失败：url 地址不符合要求的格式！')
            return redirect(url_for('home'))

        else:
            author_name = url_hostname.partition('.')[0]
            book_name = url_path.split('/')[1]
    
            # 记录作者信息
            g.db.execute("INSERT IGNORE INTO Author(ghName) VALUES(%s)", author_name)
            author_id = g.db.get("SELECT * from Author WHERE ghName=%s", author_name).id
    
            # 记录书目信息
            g.db.execute("INSERT IGNORE INTO Book(url, name, author_id) VALUES(%s,%s,%s)", 
                url, book_name, author_id)
            book_id = g.db.get("SELECT * from Book WHERE url=%s", url).id

            # 记录订阅信息
            g.db.execute("INSERT IGNORE INTO Subscribe(user_id, book_id) VALUES(%s,%s)", 
                g.user.id, book_id)
    
    return redirect(url_for('home'))

@app.route('/remove_sub/<int:book_id>')
def remove_sub(book_id):
    '''为当前用户移除指定的订阅'''

    if not github.authorized:
        abort(401)

    g.db.execute('''DELETE FROM Subscribe
                WHERE user_id = %s AND book_id = %s''', 
                g.user.id, book_id)

    return redirect(url_for('home'))

@app.route('/login')
def login():
    '''提供github授权登录入口'''
    return render_template('login.html')

@app.route('/about')
def about():
    '''应用简介页面'''
    intro = 'MIPE introduction'
    return render_template('about.html', content=intro)

if __name__ == '__main__':
    app.run()