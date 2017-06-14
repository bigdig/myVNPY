#coding=utf-8
# author: Y.Raul
# date : 2017/5/22
# 下载tushare股票数据，并存入mongodb
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

# 其它包导入
import pymongo
import json
import time

def get_daily_data(code, date):
    """
    从tushare下载日线数据，包含字段 date, open, close, high, low, volume, code
    :param code: 
    :param date: 
    :return: 
    """
    return ts.get_k_data(code, start = date)

def write_daily_data(client, data):
    """
    将日线数据写入mongodb
    :param client: 
    :param data: 
    :return: 
    """
    #   获取数据库stockdata
    db = client.stockdata

    #   获取数据集合dailydata
    dailydata = db.dailydata

#     写入数据
    dailydata.insert(json.loads(data.to_json(orient = 'records')))



def main():

 #    获取今日日期
    date = time.strftime("%Y-%m-%d", time.localtime())
 #    date = '2017-05-19'
 #  判断日期是否为交易日
    tmp = ts.get_k_data('000001', index = True, start = date)
    if tmp.empty:
        print "{date} is not market day".format(date = date)
        return 0
 #  获取pymongo客户端
    client = pymongo.MongoClient()
#   获取股票列表
    stock_list = ts.get_stock_basics(date)
    # 取10个股票测试
    stock_list = stock_list[:10]
    # 循环写入mongodb
    for code, info in stock_list.iterrows():
        print "-------"*5
        print "Trying:{code}".format(code = code)
        print info
        # for i in range(5):
        try:
            write_daily_data(client, get_daily_data(code, date))
            print "Written:{code}".format(code = code)
        except:
            print "Retrying:{code}".format(code=code)

    return 0

if __name__ == '__main__':
    main()