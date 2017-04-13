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
    """
    套利分析类，完成以下功能：
    1、检验协整性
    2、生成套利组合
    3、绘制走势图，热力图，价差图，价差分布图
    """
    def __init__(self, data, pvalue = 0.05):
        '''
           构造函数
           :param data:  需要分析的dataframe, index为时间，列名为不同标的
           :param pvalue:  平稳性、协整性检验的判断系数, p 值越低，平稳、协整关系就越强；
           '''
        self.pvalue = pvalue
        self.data = data
        self.n = self.data.shape[1]
        self.pvalue_matrix = np.ones((self.n, self.n))
        self.stationarityRes = pd.DataFrame()
        self.keys = data.keys()
        self.test_stationarity()
        self.find_cointegration()

    def test_stationarity(self):
        """
        
        :return: 
        """
        for sub in self.data.columns:
            # print sub
            # print self.data[sub]
            adftest = adfuller(self.data[sub])  # adfuller只接收1D数组
            res = pd.Series(adftest[0:4],
                            index=['Test Statistic', 'p-value', 'Lags Used', 'Number of Observations Used'])
            for key, value in adftest[4].items():
                res['Critical Value (%s)' % key] = value
            self.stationarityRes[sub] = res

    def find_cointegration(self):
        """
        
        :return: 
        """
        pairs = []
        for i in range(self.n):
            for j in range(i+1, self.n):
                sub1 = self.data[self.keys[i]]
                sub2 = self.data[self.keys[j]]
                result = sm.tsa.stattools.coint(sub1, sub2)
                pvalue = result[1]
                self.pvalue_matrix[i, j] = pvalue
                if pvalue < 0.05:
                    pairs.append((self.keys[i], self.keys[j], pvalue))
        self.pairs = pd.DataFrame(pairs, columns=['leg1','leg2','pvalue'])
        self.pairs.sort_index(by = 'pvalue', inplace=True)
        index = np.arange(len(self.pairs))

        self.pairs['index'] = index
        self.pairs.set_index('index', inplace= True)

    def find_ols(self):
        """
        
        :return: 
        """
        coefList = []
        for line in range(len(self.pairs)):
            leg1 = self.pairs.iloc[line]['leg1']
            leg2 = self.pairs.iloc[line]['leg2']
            # print "leg1: ",leg1
            # print "leg2: ",leg2

            x = self.data[leg1]
            y = self.data[leg2]
            X = sm.add_constant(x)
            result = (sm.OLS(y, X)).fit()
            coef = result.params[1]
            # print "coef: ", coef
            coefList.append(coef)

        self.pairs['coef'] = coefList

    def plotHM(self):
        """
        
        :return: 
        """
        # print type(self.data.columns.values)
        labels = self.data.columns.values
        # print self.pvalue_matrix.shape
        sns.heatmap(1 - self.pvalue_matrix, xticklabels= labels, yticklabels= labels, cmap='RdYlGn_r', mask=(self.pvalue_matrix == 1))
        # sns.heatmap(1 - self.pvalue_matrix)
        plt.show()

    def plotPair(self, leg1, leg2):
        """
        
        :return: 
        """
        pass

if __name__=='__main__':

#  导入2008010-20170401的期货日线CSV
    fileName = u'C:\\vnpy-1.5\\vn.trader\\myVNPY\\future0817.csv'
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

    # 删除流动性差的品种
    badFluidity = ['WH','RI','LR','JR','FB','BB','PB','SF','SM','SN','BU','WR']
    for i in badFluidity:
        del df[i]
    # print df.info()
    # print df['JD']
    test = Arbitrage(df.dropna())
    # test.plotHM()
    # res1 = test.stationarityRes.T
    # print res1.ix['PM']
    # print res1[res1['p-value'] < 0.05]
    # print test.stationarityRes['PM']
    # print test.pvalue_matrix
    # print test.pairs.iloc[0]['leg1']
    test.find_ols()
    # print test.pairs

    leg1 = 'PM'
    leg2 = 'IF'
    coef = test.pairs[test.pairs.leg1 == 'PM'][test.pairs.leg2 == 'IF'].coef
    # print coef
    spread = (coef.values*df[leg1] - df[leg2])
    spreadDF = pd.DataFrame(spread).dropna()

    # print type(spread)
    spreadDF.plot()

    plt.axhline(spread.mean(), color="red", linestyle="--")
    plt.xlabel("Time");
    plt.ylabel("Stationary Series")
    plt.legend(["Stationary Series", "Mean"])
    plt.title(leg1 +'---' + leg2)
    plt.show()