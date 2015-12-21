#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIPE - web app 

采用 flask 框架
"""
import re

from flask import (Flask, request, redirect, render_template,
        session, url_for, g, flash, abort)

import torndb # A lightweight wrapper around MySQLdb

# configuration
SECRET_KEY = 'secretkey'

# create application
app = Flask(__name__)
app.debug = True
app.secret_key = SECRET_KEY

@app.before_request
def before_request():
    '''在 request 之前：
    1、建立 MySQL 数据库连接
    2、检验用户登录状态，若已登录则存入 g.user
    '''
    
    # 建立 MySQL 连接，参数：host:port, database, user, passwd
    # torndb 默认已将 charset 设为 utf-8
    g.db = torndb.Connection("localhost:3306","mipetest", "root", "")
    
    g.user = None
    if 'user_id' in session:
        g.user = g.db.get("SELECT * FROM User where id=%s", 
                        session['user_id'])
        
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
    if not g.user: 
        return redirect(url_for('login'))
    
    subs = g.db.query(
        '''SELECT book_id, url, name, ghName 
        FROM Subscribe, Book, Author
        WHERE Subscribe.book_id = Book.id
        AND Book.author_id = Author.id
        AND Subscribe.user_id = %s
        ''', session['user_id']) 
    # subs 为字典构成的列表
    # 字典的键：url, name(书名), ghName(作者的github用户名)

    return render_template('subscriptions.html',subscriptions=subs)

@app.route('/add_sub', methods=['POST'])
def add_sub():
    '''为当前用户增加一个订阅，录入作者、书目、订阅信息'''
    if 'user_id' not in session:
        abort(401)
    if request.form['new_sub']:
        url = request.form['new_sub']
        
        #TODO: url 有效性检查及格式统一
        #url 格式：https://authorname.gitbooks.io/xxx/content/

        search = re.search('//.+?\.', url)
        author_name = search.group()[2:-1] if search else ''

        #book_name = get_book_name(url) # @wp-lai
        book_name = 'python 笔记'

        # 记录作者信息
        g.db.execute("INSERT IGNORE INTO Author(ghName) VALUES(%s)", author_name)     
        author_id = g.db.get("SELECT * from Author WHERE ghName=%s", author_name).id

        # 记录书目信息
        g.db.execute("INSERT IGNORE INTO Book(url, name, author_id) VALUES(%s,%s,%s)", 
            url, book_name, author_id)
        book_id = g.db.get("SELECT * from Book WHERE url=%s", url).id

        # 记录订阅信息
        g.db.execute("INSERT IGNORE INTO Subscribe(user_id, book_id) VALUES(%s,%s)", 
            session['user_id'], book_id)
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''供用户以 github 用户名和邮箱登录'''
    if g.user:
        return redirect(url_for('home'))
    
    error = None
    login_succeed = False
    #allowed_users = ["zoomquiet", "liangpeili", "yangshaoshun", "hongzhih", "dyelaine", "yondjune", "JeremiahZhang", "whb1990111", "simple2source", "wp-lai", "shawn0lee0", "bingosummer", "Lcking", "Myself", "Wangqiaoyang", "faketooth", "sherlockhoatszx", "veratulips", "siyuany", "jasonycliu", "junjielizero", "janice-lu-zeng", "aJiea", "Cen74", "Langp618", "penguinjing", "ivanlau", "rayxiehui", "bambooom", "zoejane", "WhaleChen", "xiaoyuer", "jameszhou89", "picklecai", "scottming", "4plus-ma", "liangchaob", "xpgeng", "huijuannan", "tiezipy", "sunoonlee", "Awlter", "conn820", "lixiguangzhou", "jimmy0717", "chuxueyou", "fqlxxxxx", "Raffia", "chenyan423", "kristain630", "gezizouzou", "happylumia", "Sokratesjr", "wuxianliang", "xiangshan", "lk1879", "hysic", "jorylu", "Eloisechou1", "PursuitCane", "s32n", "tttv", "xiaopan918", "lifegao12345", "LishuaiBeijing", "liznut", "mqyqlx", "Perter1990", "peter1990", "lvjiu", "wo343096281", "hanbing718", "DoSolDo", "JQ-K", "luoquan19", "tian1718", "muzakkk", "theorem0108", "jane325", "angdali", "summer724", "andreachin", "arctic-snow", "CherHu", "wwshen", "ziz9", "jiaoqing", "tedxt", "csyuking1989", "haruhi99", "SunXiaoSheng", "imxdxd", "buermen", "AaronCopperfield", "Iris-Di", "YFantasy", "Sherrywangintj", "henryopenmind", "feilalala", "rusell123", "lotusofblue", "zhiyuanlife", "jinxiaochong", "zou23cn", "LIUJISHEN", "zhouqian3", "liangdl", "liya1704", "StoryTelr", "zengyumi", "hujianfei1989", "Inspirabbits", "xiangzhendong", "cxiaodian", "zjuguxi", "demonmax", "wayson1990", "William-Shen", "RichardSZ", "shuliw", "crazy-tea", "Jessicamiejiu", "Cloudtree11", "vickyzou", "OctoberEmma", "wong-github", "nicoleyesnicole", "Nicoleyesnicole", "leonpak", "linttutu", "snatching", "dougherty930", "mjy2", "suluren", "wzzlj", "ibrother", "jaspereclipse", "ddtnt", "demichen0824", "Demi", "doreenduo43", "iBarbabob", "mac-naxin", "zoewang91", "Ericmio", "Normanplus", "soul2867", "mazichen", "Acural", "baicaiby", "nightie", "langp618", "lethinkrong", "beelives", "cupid668", "wanderingdopamine", "lyltj2010", "mastertaochao", "dayuhomes", "xkuang", "kingking", "chcaravalle", "zhangyongyu", "meleslilijing", "zhuzuojun", "waldlecai", "Xiangfeiyin", "ouyangzhiping", "YixuanFranco", "cnfeat", "ishanshan", "ZoomQuiet", "chientung91", "Azeril", "cp4", "wwulfric", "csufuyi", "badboy315", "aa", "ss", "dd"]
        
    if request.method == 'POST':
        gh_name = request.form['gh_name']
        email = request.form['email']
        existing_user = g.db.get("SELECT * FROM User where ghName=%s", gh_name)
        if not gh_name:
            error = u'Github 用户名不能为空'
        elif not email:
            error = u'Email 不能为空'
        elif existing_user == None:
            #if gh_name in allowed_users:
            if True:
                session['user_id'] = g.db.insert(
                    "INSERT INTO User (ghName, email) VALUES (%s, %s)", 
                    gh_name, email) #按 torndb 方式，传入参数时不用括号

                login_succeed = True
            else:
                error = u'此 github 用户名暂无登录权限'
        else:
            if email == existing_user.email:
                session['user_id'] = existing_user.id
                login_succeed = True
            else:
                error = u'Email 与 github 用户名不匹配'
    if login_succeed:
    	return redirect(url_for('home'))
    else:
    	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    '''供当前用户退出登录'''
    session.pop('user_id', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()