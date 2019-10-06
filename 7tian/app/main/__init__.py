from flask import Blueprint
main = Blueprint("main",__name__)   #创建蓝图
from . import views     #这个导入执行后惠志兴整个views视图函数

