#coding=utf-8
# author: Y.Raul
# date : 2017/7/21
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


from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

from  arbitrage import *

# ddd是你想绘制函数关系图的py文件
graphviz = GraphvizOutput(output_file=r'./trace_detail.png')
# 这里直接输入ddd.py里面的函数就可以直接绘制出来了，打开trace_detail.png就能看到了
with PyCallGraph(output=graphviz):
    main()
from PIL import Image
img = Image.open(r'./trace_detail.png')
img.show()