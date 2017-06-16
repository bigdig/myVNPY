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
import datetime

# 默认空值
EMPTY_STRING = ''
EMPTY_UNICODE = u''
EMPTY_INT = 0
EMPTY_FLOAT = 0.0

########################################################################
class BarData(object):
    """K线数据"""
    # ----------------------------------------------------------------------
    def __init__(self):
        self.date = EMPTY_STRING  # bar开始的时间，日期
        self.open = EMPTY_FLOAT  #
        self.close = EMPTY_FLOAT
        self.high = EMPTY_FLOAT
        self.low = EMPTY_FLOAT
        self.volume = EMPTY_INT  # 成交量
        self.code = EMPTY_STRING  # 代码


def get_daily_data(code, date, ktype = 'D' ):
    """
    从tushare下载日线数据，包含字段 date, open, close, high, low, volume, code
    :param code:
    :param date:
    :param ktype: 默认日K线
    :return:
    """
    return ts.get_k_data(code, start = date, ktype = ktype)

def write_daily_data(client, data, ktype = 'D'):
    """
       将K线数据写入mongodb
    :param client:
    :param data:
    :param ktype: 默认日K线
    :return:
    """

    if ktype in ['D','W','M']:
        timeFormat = '%Y-%m-%d'
    elif ktype in ['5','15','30','60']:
        timeFormat = '%Y-%m-%d %H:%M'
    else:
        print "{ktype} is not valid".format(ktype = ktype)
        return 0

    #   获取数据库stockdata
    db = client.stockdata

    #   获取数据集合dailydata
    dailydata = db.dailydata

    print data.head()
    print timeFormat
    start = time.time()
    print u'开始读取数据插入到数据库中'

    # 生成K线bar实例
    for values in data.values:
        bar = BarData()
        bar.date = datetime.datetime.strptime(values[0],timeFormat)
        bar.open = values[1]
        bar.close = values[2]
        bar.high = values[3]
        bar.low = values[4]
        bar.volume = values[5]
        bar.code = values[6]

        # bar.date = datetime.strptime(d['Date'], '%Y/%m/%d').strftime('%Y%m%d')
        # bar.time = d['Time']
        # bar.datetime = datetime.strptime(bar.date + ' ' + bar.time, '%Y%m%d %H:%M:%S')
        # bar.volume = d['TotalVolume']

        # flt = {'date': bar.date}
        print bar.__dict__
        # dailydata.insert({'$set': bar.__dict__})
        dailydata.insert(bar.__dict__)
        print bar.date

    print u'插入完毕，耗时：%s秒' % (time.time() - start)

#     写入数据
#     dailydata.insert(json.loads(data.to_json(orient = 'records')))



def main():

 #    获取今日日期
 #    date = time.strftime("%Y-%m-%d", time.localtime())
    date = '2017-06-15'
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
    stock_list = stock_list[:2]
    # stock_list = ['300607','600728']
    # 循环写入mongodb
    for code, info in stock_list.iterrows():
        print "-------"*5
        print "Trying:{code}".format(code = code)
        # print info
        # for i in range(5):
        try:
            write_daily_data(client, get_daily_data(code, date,'5'),'5')
            print "Written:{code}".format(code = code)
        except:
            print "Retrying:{code}".format(code=code)


    # write_daily_data(client, get_daily_data('300607', date))
    return 0

if __name__ == '__main__':
    main()