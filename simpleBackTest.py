#coding=utf-8
# author: Y.Raul
# date : 2017/4/20
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


class SimpleBackTest(object):
    """
    
    """
    def __init__(self, data, benchmarkFlag = False):
        self.data = data
        # self.benchmarkFlag = benchmarkFlag
        # 计算每天的仓位，当天持有上证指数时，仓位为1，当天不持有上证指数时，仓位为0
        self.data['todayPos'] = self.data['sig'].shift(1)
        self.data['todayPos'].fillna(method='ffill', inplace=True)

        if benchmarkFlag:
            change = 'benchmark'
        else:
            change = 'close'
        self.data['change'] = self.data[change].pct_change()

    def calRet(self):
        """
        
        :return: 
        """
        index_data['资金指数'] = (index_data['change'] * index_data['当天的仓位'] + 1.0).cumprod()
        initial_idx = index_data.iloc[0]['close'] / (1 + index_data.iloc[0]['change'])
        index_data['资金指数'] *= initial_idx


    def plotRet(self):
        pass


def turtle(data, N1 = 20, N2 = 10 ):
    """
    海龟法则,当收盘价大于最近N1天的最高价时买入，当收盘价低于最近N2天的最低价时卖出
    这两个参数可以自行调整大小，但是一般N1 > N2
    :param data: 
    :param N1:  
    :param N2: 
    :return: 
    """
    # 通过rolling_max方法计算最近N1个交易日的最高价
    data['maxN1'] = pd.rolling_max(data['high'], N1)
    # 对于上市不足N1天的数据，取上市至今的最高价
    data['maxN1'].fillna(value=pd.expanding_max(data['high']), inplace=True)

    # 通过相似的方法计算最近N2个交易日的最低价
    data['minN2'] = pd.rolling_min(data['low'], N1)
    data['minN2'].fillna(value=pd.expanding_min(data['low']), inplace=True)

    # 若当天的【close】> 昨天的【maxN1】时，将【收盘发出的信号】设定为1
    buy_index = data[data['close'] > data['maxN1'].shift(1)].index
    data.loc[buy_index, 'sig'] = 1

    # 若当天的【close】< 昨天的【最近N2个交易日的最低点】时，将【收盘发出的信号】设定为0
    sell_index = data[data['close'] < data['minN2'].shift(1)].index
    data.loc[sell_index, 'sig'] = 0

    return data['sig']

    

if __name__ == '__main__':

    # 设置回测参数
    code = '000001'
    start = '2006-01-01'
    end = '2016-12-31'
    index = True
    # 沪深300指数是2005年4月8日期设立
    benchmark = '000300'
    
    # 获取数据
    data = ts.get_k_data(code,start = start, end = end, index = index )[['date', 'open','high', 'low', 'close']]
    # 获取 benchmark
    data2 = ts.get_k_data(benchmark,start = start, end = end, index = index )[['date', 'close']]
    data2.columns = ['date', 'benchmark']
    
    data = data.merge(right = data2, on = 'date')
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace =  True)
    
    data['sig'] = turtle(data)
    print data['sig'].head()

    bt = SimpleBackTest(data)