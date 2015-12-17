# -*- coding: utf-8 -*-
"""
定义 flask app 的路由
"""

from flask import (Flask, request, redirect, render_template,
        session, url_for, g, flash, abort)

import db_user as dbu

SECRET_KEY = 'secretkey'

app = Flask(__name__)
app.debug = True

@app.before_request
def before_request():
    '''检验用户登录状态，若已登录则存入 flask.g'''
    g.user = None
    if 'user_id' in session:
        g.user = dbu.get_user_by_id(session['user_id'])

@app.route('/')
def manage_subs():
    '''显示用户订阅管理面板，可以查看、添加或删除订阅
    若用户未登录，则重定向到登录页面
    '''
    if not g.user: 
        return redirect(url_for('login'))
    
    #subs = dbu.get_subs(session['user_id']) 
    subs = ['first gitbook', 'second gitbook', 'third gitbook'] #测试用

    return render_template('subscriptions.html',subscriptions=subs)

@app.route('/add_sub', methods=['POST'])
def add_sub():
    '''为当前用户增加一个订阅'''
    if 'user_id' not in session:
        abort(401)
    if request.form['new_sub']:
        new_sub = request.form['new_sub']
        #dbu.insert_sub(new_sub, session['user_id'])
    return redirect(url_for('manage_subs'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''供用户以 github 用户名和邮箱登录'''
    if g.user:
        return redirect(url_for('manage_subs'))
    
    error = None
    allowed_users = ["zoomquiet", "liangpeili", "yangshaoshun", "hongzhih", "dyelaine", "yondjune", "JeremiahZhang", "whb1990111", "simple2source", "wp-lai", "shawn0lee0", "bingosummer", "Lcking", "Myself", "Wangqiaoyang", "faketooth", "sherlockhoatszx", "veratulips", "siyuany", "jasonycliu", "junjielizero", "janice-lu-zeng", "aJiea", "Cen74", "Langp618", "penguinjing", "ivanlau", "rayxiehui", "bambooom", "zoejane", "WhaleChen", "xiaoyuer", "jameszhou89", "picklecai", "scottming", "4plus-ma", "liangchaob", "xpgeng", "huijuannan", "tiezipy", "sunoonlee", "Awlter", "conn820", "lixiguangzhou", "jimmy0717", "chuxueyou", "fqlxxxxx", "Raffia", "chenyan423", "kristain630", "gezizouzou", "happylumia", "Sokratesjr", "wuxianliang", "xiangshan", "lk1879", "hysic", "jorylu", "Eloisechou1", "PursuitCane", "s32n", "tttv", "xiaopan918", "lifegao12345", "LishuaiBeijing", "liznut", "mqyqlx", "Perter1990", "peter1990", "lvjiu", "wo343096281", "hanbing718", "DoSolDo", "JQ-K", "luoquan19", "tian1718", "muzakkk", "theorem0108", "jane325", "angdali", "summer724", "andreachin", "arctic-snow", "CherHu", "wwshen", "ziz9", "jiaoqing", "tedxt", "csyuking1989", "haruhi99", "SunXiaoSheng", "imxdxd", "buermen", "AaronCopperfield", "Iris-Di", "YFantasy", "Sherrywangintj", "henryopenmind", "feilalala", "rusell123", "lotusofblue", "zhiyuanlife", "jinxiaochong", "zou23cn", "LIUJISHEN", "zhouqian3", "liangdl", "liya1704", "StoryTelr", "zengyumi", "hujianfei1989", "Inspirabbits", "xiangzhendong", "cxiaodian", "zjuguxi", "demonmax", "wayson1990", "William-Shen", "RichardSZ", "shuliw", "crazy-tea", "Jessicamiejiu", "Cloudtree11", "vickyzou", "OctoberEmma", "wong-github", "nicoleyesnicole", "Nicoleyesnicole", "leonpak", "linttutu", "snatching", "dougherty930", "mjy2", "suluren", "wzzlj", "ibrother", "jaspereclipse", "ddtnt", "demichen0824", "Demi", "doreenduo43", "iBarbabob", "mac-naxin", "zoewang91", "Ericmio", "Normanplus", "soul2867", "mazichen", "Acural", "baicaiby", "nightie", "langp618", "lethinkrong", "beelives", "cupid668", "wanderingdopamine", "lyltj2010", "mastertaochao", "dayuhomes", "xkuang", "kingking", "chcaravalle", "zhangyongyu", "meleslilijing", "zhuzuojun", "waldlecai", "Xiangfeiyin", "ouyangzhiping", "YixuanFranco", "cnfeat", "ishanshan", "ZoomQuiet", "chientung91", "Azeril", "cp4", "wwulfric", "csufuyi", "badboy315", "aa", "ss", "dd"]
    
    if request.method == 'POST':
        gh_name = request.form['gh_name']
        email = request.form['email']
        if not gh_name:
            error = u'Github 用户名不能为空'
        elif not email:
            error = u'Email 不能为空'
        elif dbu.get_user_by_name(gh_name) == None:
            if gh_name in allowed_users:
                dbu.insert_user(gh_name, email)
                session['user_id'] = dbu.get_user_by_name(gh_name)['id']
                return redirect(url_for('manage_subs'))
            else:
                error = u'此 github 用户名暂无登录权限'
        else:
            if email == dbu.get_user_by_name(gh_name)['email']:
                session['user_id'] = dbu.get_user_by_name(gh_name)['id']
                return redirect(url_for('manage_subs'))
            else:
                error = u'Email 与 github 用户名不匹配'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    '''供当前用户退出登录'''
    session.pop('user_id', None)
    return redirect(url_for('login'))

app.secret_key = SECRET_KEY