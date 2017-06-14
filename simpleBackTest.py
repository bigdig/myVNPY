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
    简单回测框架：
    1、根据开仓（1）、平仓（0）信号（Sg），生成当日仓位（Pos）
    2、T日生成sig，T+1日持有仓位
    3、以收盘价(close)的日涨跌幅(change)计算单位资金收益(money)
    4、默认策略收益(strategy)对比自身持有收益
    """
    def __init__(self, data, benchmarkFlag = False):
        """   
        :param data:  回测数据，index = date, columns =  open, high, low, close, sig 
        :param benchmarkFlag:  True时，则引入收益的benchmark，在data中增加 benchmark列；
        """
        self.data = data
        self.benchmarkFlag = benchmarkFlag
        self.data['change'] = self.data['close'].pct_change()
        # 计算每天的仓位，当天持有上证指数时，仓位为1，当天不持有上证指数时，仓位为0
        self.data['Pos'] = self.data['Sig'].shift(1)
        self.data['Pos'].fillna(method='ffill', inplace=True)


    def runBackTest(self):
        """
        回测
        :return: 
        """
        # 当仓位(Pos)为1时，买入，当仓位(Pos)为0时，卖出；
        # 计算累计单位收益
        self.data['strategy'] = (self.data['change'] * self.data['Pos'] + 1.0).cumprod()
        self.data['market'] = (self.data['change'] + 1).cumprod()

        # 如果需要对比benchmark，则计算其累计收益
        if self.benchmarkFlag:
            self.data['benchmarkRet'] = self.data['benchmark_close'].pct_change()
            self.data['benchmark'] = (self.data['benchmarkRet'] +1.0).cumprod()

    def  calYearRT(self):
        """
        计算年化收益
        :return: 年化收益
        """
        # ==========计算每年市场的收益的收益
        self.data['strategyRet'] = self.data['change'] * self.data['Pos']
        # self.data['marketRet'] = self.data['change']
        if self.benchmarkFlag:
            year_rtn = self.data[['strategyRet', 'benchmarkRet']]. \
                resample('A').apply(lambda x: ((x + 1.0).prod() - 1.0) * 100)
        else:
            year_rtn = self.data[['change', 'strategyRet']]. \
                resample('A').apply(lambda x: ((x + 1.0).prod() - 1.0) * 100)

        return year_rtn

    def plotRet(self):
        """
         绘制单位收益走势图(strategy, market, benchmark)
        :return: 
        """
        if self.benchmarkFlag:
            self.data[['strategy', 'benchmark']].plot()
        else:
            self.data[['strategy', 'market']].plot()
        plt.ylabel("Unit Return")
        plt.xlabel("Date")
        plt.grid(True)
        plt.show()

def turtle(data, N1 = 20, N2 = 10 ):
    """
    海龟法则,当收盘价大于最近N1天的最高价时买入，当收盘价低于最近N2天的最低价时卖出
    这两个参数可以自行调整大小，但是一般N1 > N2
    :param data: 
    :param N1:  
    :param N2: 
    :return: 
    """
    # print "in turtle"
    # 通过rolling_max方法计算最近N1个交易日的最高价
    # data['maxN1'] = pd.rolling_max(data['high'], N1)
    data['maxN1'] = data['high'].rolling(window=N1, center=False).max()
    # 对于上市不足N1天的数据，取上市至今的最高价
    # data['maxN1'].fillna(value=pd.expanding_max(data['high']), inplace=True)
    data['maxN1'].fillna(value=data['high'].expanding(min_periods=1).max(), inplace=True)
    
    # 通过相似的方法计算最近N2个交易日的最低价
    # data['minN2'] = pd.rolling_min(data['low'], N1)
    data['minN2'] = data['low'].rolling(window=N2, center=False).min()
    # data['minN2'].fillna(value=pd.expanding_min(data['low']), inplace=True)
    data['minN2'].fillna(value=data['low'].expanding(min_periods=1).min(), inplace=True)

    # 若当天的【close】> 昨天的【maxN1】时，将【收盘发出的信号】设定为1
    buy_index = data[data['close'] > data['maxN1'].shift(1)].index
    data.loc[buy_index, 'sig'] = 1

    # 若当天的【close】< 昨天的【最近N2个交易日的最低点】时，将【收盘发出的信号】设定为0
    sell_index = data[data['close'] < data['minN2'].shift(1)].index
    data.loc[sell_index, 'sig'] = 0

    return data['sig']

    


if __name__ == '__main__':
    # print "in main"
    # 设置回测参数
    code = '510050' #50ETF
    start = '2006-01-01'
    end = '2016-12-31'
    # 若回测数据为指数，则为True，其他为False
    index = False
    # 若benchmark数据为指数，则为True,其他为False
    benchmarkIndex = True
    # 沪深300指数是2005年4月8日期设立
    benchmark = '000300'

    dataFile = "./{code}_data.csv".format(code = code)
    # print dataFile
    import os
    if not os.path.exists(dataFile):
    # 获取回测数据
        data = ts.get_k_data(code,start = start, end = end, index = index )[['date', 'open','high', 'low', 'close']]
    # 获取 benchmark
        data2 = ts.get_k_data(benchmark,start = start, end = end, index = benchmarkIndex )[['date', 'close']]
        data2.columns = ['date', 'benchmark_close']
        data = data.merge(right = data2, on = 'date')
        data.to_csv(dataFile, index_label= 'date')
    else:
        data = pd.read_csv(dataFile)

    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    data['Sig'] = turtle(data)

    bt = SimpleBackTest(data, True)
    bt.runBackTest()
    bt.plotRet()
    print bt.calYearRT()