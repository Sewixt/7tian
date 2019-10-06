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

#########################################分页器
class Pager:
    def __init__(self,data,page_size):   #分页数据，每页数据
        self.data = data
        self.page_size = page_size
        self.is_start = False       #是否为首页
        self.is_end = False         #是否为尾页
        self.page_count = len(data)         #总数据
        self.next_page = 0          #下一页
        self.last_page = 0          #上一页
        self.page_number = self.page_count/page_size        #总页数
        #(data + page_size-1) // page_size
        if self.page_number == int(self.page_number):
            self.page_number = int(self.page_number)
        else:
            self.page_number = int(self.page_number)+1         #不能整除直接加1
        self.page_range = range(1,self.page_number+1)
    def page_data(self,page):
        """
                返回分页数据
                :param page: 页码
                page_size = 10
                1    offect 0  limit(10)
                2    offect 10 limit(10)
                page_size = 10
                1     start 0   end  10
                2     start 10   end  20
                3     start 20   end  30
                """
        self.next_page = int(page) + 1
        self.last_page = int(page) - 1
        if page <= self.page_range[-1]:
            page_start = (page - 1)*self.page_size
            page_end = page * self.page_size
            #data = self.data.offset(page_start).limit(self.page_size)
            data = self.data[page_start:page_end]
            if page == 1:
                self.is_start = True
            else :
                self.is_start = False
            if page == self.page_range[-1]:
                self.is_end = True
            else:
                self.is_end = False
        else:
            data = ["没有数据"]
        return data



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

######################################请假条
@main.route("/holiday_leave/",methods=["POST","GET"])
def holiday_leave():
    if request.method == "POST":
        data =request.form
        username = data.get("username")
        request_type = data.get("request_type")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        phone = data.get("phone")
        request_description = data.get("request_description")

        leave = Leave()
        leave.request_id = request.cookies.get("id")
        leave.request_name = username
        leave.request_type = request_type
        leave.request_start_time = start_time
        leave.request_end_time = end_time
        leave.request_phone = phone
        leave.request_description = request_description
        leave.request_status = "0"
        leave.save()
        return redirect("/leave_list/1/")
    return render_template("holiday_leave.html")

@main.route("/leave_list/<int:page>/")
def leave_list(page):
    leaves = Leave.query.all()   ##获取所有请假人员信息
    pager = Pager(leaves,2)     ##实例化Pager
    page_data = pager.page_data(page)       #
    return render_template("leave_list.html",**locals())

class Calender:
    def __init__(self,month = "now"):
        self.result = [ ]
        big_month = [1,3,5,7,8,10,12]
        small_month = [4,6,9,11]
        now = datetime.datetime.now()
        if month == "now":
            month = now.month
            first_date = datetime.datetime(now.year,now.month,1,1)
        else:
            first_date = datetime.datetime(now.year,month,1,1)

        if month in big_month:
            day_range = range(1,32)
        elif month in small_month:
            day_range = range(1,31)
        else:
            day_range = range(1,30)

        #获取指定月的天数
        self.day_range = list(day_range)
        first_week = first_date.weekday() #获取指定月1号是周几

        line1 = [ ]
        for j in range(first_week):
            line1.append(" ")
        for k in range(7-first_week):
            line1.append(str(self.day_range.pop(0)))
        self.result.append(line1)

        while self.day_range:
            line = [ ]    #第二周及往后的数据
            for i in range(7):
                if len(line) < 7 and self.day_range:
                    line.append(str(self.day_range.pop(0)))
                else:
                    line.append(" ")
            self.result.append(line)

    def return_month(self):
        #返回列表嵌套的日历
        return self.result

    def print_month(self):
        ###按照日历格式打印样式
        print("星期一  星期二  星期三  星期四  星期五  星期六 星期日")
        for line in self.result:
            for day in line:
                day = day.center(6)
                print(day, end="  ")
            print()

@main.route("/user_info/")
def user_info():
    calendar = Calender().return_month()
    now = datetime.datetime.now()
    head = "北京优就业%s年%s月份课表"%(now.year,now.month)
    return render_template("user_info.html",**locals())


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