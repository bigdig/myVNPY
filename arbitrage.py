# encoding: UTF-8
# auther: Y.Raul

# 系统包导入
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from datetime import datetime

# 绘图包导入
import  matplotlib.pyplot as plt
import seaborn as sns

#分析包导入
import talib as ta

class FindPairs(object):
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
        self.find_stationarity()
        self.find_cointegration()
        self.find_coef()

    def find_stationarity(self):
        """
        平稳性检验，p-value小于0.05则认为平稳
        :return: stationarityRes中保留检验结果
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
        协整性检验，p-value小于0.05则认为平稳。
        :return: pairs中保存配对结果
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

        # pair配对结果
        self.pairs = pd.DataFrame(pairs, columns=['leg1','leg2','pvalue'])
        self.pairs.sort_values(by = 'pvalue', inplace=True)
        index = np.arange(len(self.pairs))

        self.pairs['index'] = index
        self.pairs.set_index('index', inplace= True)

    def find_coef(self):
        """
        计算配对系数coef
        :return: pairs中增加配对系数coef列，对应pair的spread为 (coef*leg1 - leg2)
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

    def plotHeatmap(self):
        """
        根据协整性检验的结果绘制热力图
        :return: 
        """
        # print type(self.data.columns.values)
        labels = self.data.columns.values
        # print self.pvalue_matrix.shape
        sns.heatmap(1 - self.pvalue_matrix, xticklabels= labels, yticklabels= labels, cmap='RdYlGn_r', mask=(self.pvalue_matrix == 1))
        # sns.heatmap(1 - self.pvalue_matrix)
        plt.show()

    def plotPair(self, leg1, leg2,mul = 2 ):
        """
        绘制leg1,leg2走势图，spread价差回归图，spread价差分布图
        :param leg1: 
        :param leg2: 
        :param mul: spread的上下限标准差倍数，默认为2
        :return: 
        """
        tmp = self.pairs[self.pairs.leg1 == leg1]
        coef =  (tmp[tmp.leg2 == leg2].coef).values
        # print coef

        legs = pd.DataFrame()
        legs[leg1] = self.data[leg1]
        legs[leg2] = self.data[leg2]
        legs['spread'] = (coef * legs[leg1] - legs[leg2])
        spreadMean = legs['spread'].mean()
        spreadStd = legs['spread'].std()

        # spreadZ为价差的标准化Z分数
        legs['spreadZ'] = (legs['spread'] - spreadMean)/spreadStd
        idmax = legs['spread'].idxmax()
        idmin = legs['spread'].idxmin()



        print  "value of max: ", legs['spread'].ix[idmax]
        print  "value of min: ", legs['spread'].ix[idmin]

        # print type(idmax)
        # 绘图初始设置
        fig, axes = plt.subplots(3, 1, figsize=(20, 12))

        # 绘制leg1,leg2走势图
        legs[[leg1,leg2]].plot(ax = axes[0])
        axes[0].grid(True)
        axes[0].set_ylabel('Settle Price')
        axes[0].set_title(leg1 + u' and ' + leg2)

        # 绘制价差spread走势图
        # spreadMid = spreadMean
        spreadUp = spreadMean + mul* spreadStd
        spreadDown = spreadMean - mul* spreadStd

        legs['spread'].plot(ax = axes[1], color = 'k')
        axes[1].axhline(spreadMean, color="red", linestyle="--")
        axes[1].axhline(spreadUp, color="b", linestyle="--")
        axes[1].axhline(spreadDown, color="b", linestyle="--")

        axes[1].legend(["Spread", "Mean"])
        axes[1].set_ylabel('Spread Price')
        outlier = [(idmax, round(legs['spread'].ix[idmax],2)), (idmin, round(legs['spread'].ix[idmin],2))]

        spread = legs['spread']
        for date,label in outlier:
            axes[1].annotate(label, xy=(date, spread.asof(date)), xytext = (date, spread.asof(date) + 200),
                              arrowprops=dict(facecolor='R'),
                              horizontalalignment='left', verticalalignment='top')
        # 绘制spread的分布图
        sns.distplot(legs['spreadZ'], bins=50, ax = axes[2])
        axes[2].set_ylabel('Hist')
        # legs['spread'].hist(bins = 50, ax =axes[2])
        plt.subplots_adjust(hspace=0.3)
        plt.show()

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
    # 将index更换为DatetimeIndex
    df.set_index(pd.to_datetime(df.index.values), inplace=True)
    # print df.info()

    # df.dropna(inplace=True)
    # print df['JD']

    test = FindPairs(df.dropna())
    print test.pairs
    leg1 = 'PM'
    leg2 = 'M'
    test.plotPair(leg1,leg2)
