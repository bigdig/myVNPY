# encoding: UTF - 8
# 系统包导入
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

# 绘图包导入
import  matplotlib.pyplot as plt
import seaborn as sns

#分析包导入
import talib as ta
class Arbitrage(object):
    '''
    套利分析类，完成以下功能：
    1、检验协整性
    2、生成套利组合
    3、绘制走势图，热力图，价差图，价差分布图
    '''
    def __init__(self, data, pvalue = 0.05):
        '''
        构造函数
        :param data:  需要分析的dataframe, index为时间，列名为不同标的
        :param pvalue:  平稳性、协整性检验的判断系数, p 值越低，平稳、协整关系就越强；
        '''
            self.pvalue = pvalue
            self.data = data
            self.n = self.data.shape[1]
            self.pvalue_matrix = np.ones((n, n))
            self.stationarityRes = pd.DataFrame()
            self.keys = data.keys()
            self.pairs = []

    def test_stationarity(self):
        '''
        检验data中序列的平稳性
        :param self: 
        '''
        for  sub in self.data.columns:

            adftest = adfuller(self.data[sub]) #adfuller只接收1D数组
            res = pd.Series(adftest[0:4],
                           index=['Test Statistic', 'p-value', 'Lags Used', 'Number of Observations Used'])
            for key, value in adftest[4].items():
                res['Critical Value (%s)' % key] = value
            self.stationarityRes[sub] = res

    def find_cointegration(self):
        '''
        检验data中的协整性
        :param self: 
        :return: 返回协整性矩阵
        '''
        for i in range(self.n):
            for j in range(i+1, self.n):
                sub1 = self.data[self.keys[i]]
                sub2 = self.data[self.keys[j]]
                result = sm.tsa.stattools.coint(sub1, sub2)
                pvalue = result[1]
                self.pvalue_matrix[i, j] = pvalue
                if pvalue < 0.05:
                    self.pairs.append((self.keys[i], self.keys[j], pvalue))


if __name__=='__main__':

#  导入2008010-20170401的期货日线CSV
    fileName = u'C:\\vnpy-1.5\\vn.trader\My Module\\future0817.csv'
    future0817 = pd.read_csv(fileName, index_col='tradeDate')
    # print future0817.info()
    # 合约列表
    contractList = (future0817['contractObject'].drop_duplicates()).values
    # print contractList
    # 考虑收盘价
    data = future0817[['contractObject', 'settlePrice']].dropna()
    # 数据清理
    con = list(set(data['contractObject']))
    df = pd.DataFrame()
    for i in con:
        df2 = pd.DataFrame(data[data['contractObject']==i]['settlePrice'])
        df2.columns = [i]
        df = pd.concat([df,df2], axis=1)
    print df.info()
    # 删除流动性差的品种
    badFluidity = ['WH','RI','LR','JR','FB','BB','PB','SF','SM','SN','BU','WR']
    for i in badFluidity:
        del df[i]