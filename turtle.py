# -*- coding: utf-8 -*-
"""
@量化交流QQ群:461470781，欢迎交流
"""
import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
import seaborn

# ==========导入上证指数的原始数据
code = '510050'
indexFlg = False
start = '2016-01-01'
#通过tushare获取上证指数数据
index_data = ts.get_k_data(code, start, index = indexFlg)
index_data = index_data[['date', 'open', 'close', 'high', 'low']]
# 计算当日收盘与昨日收盘的涨跌幅
index_data['change'] = index_data['close'].pct_change()
# 将date转换为datetime格式
index_data['date'] = pd.to_datetime(index_data['date'])

# ==========计算海龟交易法则的买卖点
# 设定海龟交易法则的两个参数，当收盘价大于最近N1天的最高价时买入，当收盘价低于最近N2天的最低价时卖出
# 这两个参数可以自行调整大小，但是一般N1 > N2
N1 = 20
N2 = 10

# 通过rolling_max方法计算最近N1个交易日的最高价
# index_data['maxN1'] =  pd.rolling_max(index_data['high'], N1)
index_data['maxN1']  = index_data['high'] .rolling(window=N1,center=False).max()
# 对于上市不足N1天的数据，取上市至今的最高价
# index_data['maxN1'].fillna(value=pd.expanding_max(index_data['high']), inplace=True)
index_data['maxN1'].fillna(value=index_data['high'].expanding(min_periods=1).max(), inplace=True)

# 通过相似的方法计算最近N2个交易日的最低价
# index_data['minN2'] =  pd.rolling_min(index_data['low'], N1)
index_data['minN2']  = index_data['low'] .rolling(window=N2,center=False).min()
# index_data['minN2'].fillna(value=pd.expanding_min(index_data['low']), inplace=True)
index_data['minN2'].fillna(value=index_data['low'].expanding(min_periods=1).min(), inplace=True)

# 当当天的【close】> 昨天的【最近N1个交易日的最高点】时，将【收盘发出的信号】设定为1
buy_index = index_data[index_data['close'] > index_data['maxN1'].shift(1)].index
index_data.loc[buy_index, 'Sig'] = 1

# 当当天的【close】< 昨天的【最近N2个交易日的最低点】时，将【收盘发出的信号】设定为0
sell_index = index_data[index_data['close'] < index_data['minN2'].shift(1)].index
index_data.loc[sell_index, 'Sig'] = 0

# 计算每天的仓位，当天持有上证指数时，仓位为1，当天不持有上证指数时，仓位为0
index_data['pos'] = index_data['Sig'].shift(1)
index_data['pos'].fillna(method='ffill', inplace=True)


# 当仓位为1时，买入上证指数，当仓位为0时，空仓。计算从2010-01-01至今的资金指数
index_data['strategy'] = (index_data['change'] * index_data['pos'] + 1.0 ).cumprod()
#
index_data['market'] =( index_data['change'] + 1 ).cumprod()

# index_data['market'] =( index_data['close']/index_data['close'].shift(1) ).cumprod()
# index_data['strategy'] = (index_data['market'] * index_data['pos'] ).cumprod()

# initial_idx = index_data.iloc[0]['close'] / (1 + index_data.iloc[0]['change'])
# index_data['strategy'] *= initial_idx
# 绘制收益图
index_data.set_index('date', inplace= True)
(index_data[['strategy', 'market']] * 100.0).plot(title = 'Turtle System')
plt.show()

# 输出数据到指定文件
index_data[[ 'high', 'low', 'close', 'change', 'maxN1',
            'minN2', 'pos', 'strategy', 'market']].to_csv('turtle.csv', index_label = 'date' )


# ==========计算每年指数的收益以及海龟交易法则的收益
index_data['ret'] = index_data['change'] * index_data['pos']

# year_rtn = index_data[['change', 'ret']].\
#                resample('A', how=lambda x: (x+1.0).prod() - 1.0) * 100
year_rtn = index_data[['change', 'ret']].\
               resample('A').apply( lambda x: ((x+1.0).prod() - 1.0) * 100)
print year_rtn