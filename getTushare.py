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

def writeLog(message, logfile = '.\\getTushare.log'):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
    with open(logfile,'a+') as f:
        f.writelines(message + '\n')


def get_daily_data(code, date, ktype = 'D' ):
    """
    从tushare下载日线数据，包含字段 date, open, close, high, low, volume, code
    :param code:
    :param date:
    :param ktype: 默认日K线
    :return:
    """
    ktypeDic = {'D': u'日', 'W':u'周', 'M':u"月", \
                '5':u'5分钟', '15':u"15分钟",'30':u'30分钟','60':'60分钟'}
    message =  u'开始下载 {date}, {code}的{ktype}行情'.format(date = date, code = code, ktype = ktypeDic[ktype])
    print message
    writeLog(message)

    start = time.time()

    try:
        data = ts.get_k_data(code, start = date, ktype = ktype)
    except Exception,e:
        print u"下载行情数据失败"
        writeLog( u"下载行情数据失败")

        message = u"错误：{ecode}".format(ecode=e)
        print message
        writeLog(message)

        return pd.DataFrame()

    message = u'下载完毕，耗时：%.3f秒' % (time.time() - start)
    print message
    writeLog(message)

    return data

def write_daily_data(client, data, ktype = 'D'):
    """
       将K线数据写入mongodb
    :param client:
    :param data:
    :param ktype: 默认日K线
    :return:
    """
    ktypeDic = {'D': u'dayData', 'W': u'weekData', 'M': u"monthData", '5': u'5mData', \
                '15': u"15mData", '30': u'30mData', '60': '60mData'}
    if ktype in ['D','W','M']:
        timeFormat = '%Y-%m-%d'
    elif ktype in ['5','15','30','60']:
        timeFormat = '%Y-%m-%d %H:%M'
    else:
        print "{ktype} is not valid".format(ktype = ktype)
        return 0

    #   获取数据库db名称
    dbName = 'tushareData'
    db = client[dbName]

    #   获取数据collection名称
    collName = ktypeDic[ktype]
    dailydata = db[collName]

    # print data.head()yyyy
    # print timeFormat

    start = time.time()
    # print start
    message = u'开始读取数据插入到数据库 {dbName}-{collName}'.format(dbName = dbName, collName = collName)
    print message
    writeLog(message)

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

        dailydata.insert(bar.__dict__)

    # print u'数据库插入完毕，耗时：%.3f秒' % (time.time() - start)
    message =  u'数据插入完毕，耗时：%.3f秒' % (time.time() - start)
    print message
    writeLog(message)

    return 1

def main(klist = ['5'],tryNum = 5):

 #    获取今日日期
    date = time.strftime("%Y-%m-%d", time.localtime())
 # ktypeDic = {'D': u'dayData', 'W': u'weekData', 'M': u"monthData", '5': u'5mData', \
 #             '15': u"15mData", '30': u'30mData', '60': '60mData'}
 #    date = '2017-06-15'
 #    ktype = 'D'
    tryNum = tryNum
 #  判断日期是否为交易日
    try:
        tmp = ts.get_k_data('000001', index = True, start = date)
    except Exception, e:
        message =  u"错误：{ecode}".format(ecode = e)
        print message
        writeLog(message)

    if tmp.empty:
        message = u"{date} 非交易日".format(date = date)
        print message
        writeLog(message)
        return 0

#  获取pymongo客户端
    client = pymongo.MongoClient()

#   获取股票列表
    try:
        stock_list = ts.get_stock_basics(date)
    except Exception, e:
        message = u"错误：{ecode}".format(ecode=e)
        print message
        writeLog(message)
        stock_list = ts.get_stock_basics()

    # 取10个股票测试
    # stock_list = stock_list[:2]
    # stock_list = ['300607','600728']

    # 循环写入mongodb



    for code, info in stock_list.iterrows():
        for ktype in klist:
            i = 1
            while i <= tryNum:
            # 循环尝试下载数据，次数为tryNum
                message = "-------" * 5
                print message
                writeLog(message)

                data = get_daily_data(code, date,ktype)

                if not data.empty:
                    break
                else:
                    i += 1
                    message = "第{i}次重新尝试下载: {code}".format(i = i,code=code)
                    print message
                    writeLog(message)
            if not data.empty:
                write_daily_data(client, data, ktype)
            else:
                message = "无法下载: {code}".format(code=code)
                print message
                writeLog(message)
    return 0

if __name__ == '__main__':

    message = "-------" * 8
    print message
    writeLog(message)

    import os
    message = u"启动任务: " + os.path.splitext(os.path.basename(__file__))[0] +' : ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print message
    writeLog(message)

    start = time.time()
    klist = ['5','15','30']
    tryNum = 5
    main(klist, tryNum)
    # print u"结束任务: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    message =   u"结束任务: " + os.path.splitext(os.path.basename(__file__))[0] +' : ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + \
               u' ,耗时：%.3f秒' % (time.time() - start)
    print message
    writeLog(message)
