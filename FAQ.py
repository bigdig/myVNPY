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

# 绘图中显示中文

from matplotlib.font_manager import FontProperties
# 字体为简体黑体，可以在文件夹选对应字体，右键属性获取名称
font = FontProperties(fname=r"C:\Windows\Fonts\\simhei.ttf", size=14)

# 解决UnicodeDecodeError: ‘ascii’ codec can’t decode byte
# 原因就是Python的str默认是ascii编码，和unicode编码冲突，就会报这个标题错误。

import sys
reload(sys)
sys.setdefaultencoding('utf8')
