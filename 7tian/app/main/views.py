#  视图文件
import os
import json
import datetime
import hashlib
import functools

from flask import jsonify
from flask import render_template
from flask import redirect
from flask import request
from flask import session


from app import api
from flask_restful import Resource
# from main import csrf
from . import main
from app.models import *




#########################################装饰器
def Log_vaild(fun):
    @functools.wraps(fun)
    def inner(*args,**kwargs):
        username = request.cookies.get("username")
        id = request.cookies.get("id","0")
        user = User.query.get(int(id))
        session_name = session.get("username")
        if user:
            if user.user_name == username and session_name == username:
                return fun(*args,**kwargs)
            else:
                return redirect("/login/")
        else:
            return redirect("/login/")
    return inner




@main.route("/base/")
def base():
    return render_template("base.html")

@main.route("/index/")
@Log_vaild
def index():
    # c = Curriculum()
    # c.c_id = "001"
    # c.c_name = "pyhon"
    # c.c_time = datetime.datetime.now()
    # c.save()
    c_list = Curriculum.query.all()
    return render_template("index.html",c_list = c_list)



############################注册

@main.route("/register/",methods=["GET","POST"])
def register():
    error_message = []
    if request.method == "POST":
        username = request.form.get("username")     #form表单提交的数据用request.form接受
        email = request.form.get("email")
        password = request.form.get("password")
        if username and email and password:
            u = User()
            u.user_name = username
            u.email = email
            u.password = set_password(password)  ######  密码加密
            u.save()
        else:
            error_message = "请输入正确的用户名，邮箱，密码"
    return render_template("register.html")

######################################设置密码
def set_password(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    # result = hashlib.md5(password.encode()).hexdigest()
    return result

#####################################登录

@main.route("/login/",methods=["GET","POST"])
def login():
    error_message = ""
    if request.method == "POST":
        form_data = request.form
        email = form_data.get("email")
        password = form_data.get("password")
        user = User.query.filter_by(email = email).first()
        if user:
            db_password = user.password
            if set_password(password) == db_password:
                response = redirect("/index/")
                response.set_cookie("username",user.user_name)
                response.set_cookie("id",str(user.id))
                response.set_cookie("email",user.user_name)
                session["username"] = user.user_name
                return response
            else:
                error_message = "密码错误"
        else:
            error_message = "用户名不存在"
    return render_template("login.html",error_message = error_message)


#####################################退出
@main.route("/logout/")
def logout():
    response = redirect("/login/")
    response.delete_cookie("username")
    response.delete_cookie("id")
    response.delete_cookie("email")
    del session["username"]
    return response









######################################






import random
def Valid_code(len=6):
    str = "0123456789"
    valid_code ="".join([random.choice(str) for i in range(len)])
    return valid_code

#
#
# if __name__ == '__main__':
#     app.run(host='127.0.0.1')