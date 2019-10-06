import wtforms
from flask_wtf import FlaskForm
from wtforms import validators

from wtforms import ValidationError

def keywords_valid(form,field):
    """
    :param form: 表单
    :param field:  字段
    这两个都不用主动传参
    """
    data = field.data #获取input内容（value）
    keywords = ["admin","GM","管理员","版主"]
    if data in keywords:
        raise ValidationError("不可以以敏感词命名")

#
