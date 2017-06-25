#coding=utf-8
# author: Y.Raul
# date : 2017/6/17
# 常见问题
# 系统包导入
import pandas as pd
import numpy as np

# 绘图包导入
import matplotlib.pyplot as plt
import seaborn as sns

#分析包导入
import talib as ta

#数据包导入
import tushare as ts

# ##################################################
# (1)绘图中显示中文
from matplotlib.font_manager import FontProperties
# 字体为简体黑体，可以在文件夹选对应字体，右键属性获取名称
font = FontProperties(fname=r"C:\Windows\Fonts\\simhei.ttf", size=14)

##############################################################
# (2)解决UnicodeDecodeError: ‘ascii’ codec can’t decode byte
# 原因就是Python的str默认是ascii编码，和unicode编码冲突，就会报这个标题错误。
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# ##################################################
# (3)python 中import问题
#import作用：
# 导入/引入一个python标准模块，其中包括.py文件、带有__init__.py文件的目录；
# __import__作用：同import语句同样的功能，但__import__是一个函数，并且只接收字符串作为参数，
# 所以它的作用就可想而知了。其实import语句就是调用这个函数进行导入工作的，import sys <==>sys = __import__('sys')

# 动态导入module，两种方法
from importlib import import_module
myModule = import_module('strategy_TripleMa')
myModule = __import__('strategy_TripleMa')
# ！！！注意，Python文件(即py文件，module,package)命名不能有'.', eg： strategy_TripleMa_v0.1，
# 可以有空格、下划线， eg: strategy_TripleMa_v 01, strategy_TripleMa_v01

# 导入当前目录下module,直接import 即可
# 绝对路径方式
import sys
sys.path.append("..")
from ctaBacktesting import *

# ##################################################
# (4)pycharm中运行程序出现nosetest，原因在于出现了test开头的函数
# settings-tools-Python Integrated Tools-Default test runner-py.test

# ##################################################
# (5)LOG写入函数
def writeLog(message, logfile = '.\\getTushare.log'):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    with open(logfile,'a+') as f:
        f.writelines(message + '\n')

# ##################################################
# (6)try...except

    try:
        tmp = ts.get_k_data('000001', index = True, start = date)
    except Exception, e:
        message =  u"错误：{ecode}".format(ecode = e)
        print message
        writeLog(message)
# ##################################################
 #  (7)str的format方法
# 位置替换
'{0},{1}'.format('kzc',18)
# 关键字替换
'{name},{age}'.format(age=18,name='kzc')
# 限定符
'{:.2f}'.format(321.33345)
'321.33'
# 千分位
'{:,}'.format(1234567890)