# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import tushare as ts
import talib as ta
import matplotlib.pyplot as plt
import seaborn

def plotStock(code, start, end):
    """
    绘制股票的收盘价、成交量、MACD指标
    :param code:
    :param start:
    :param end:
    :return:
    """
    data = ts.get_k_data(code,start = start, end = end)
    DIFF,DEA, MACD = ta.MACD(data.close.values)
    data['DIFF'] = DIFF
    data['DEA'] = DEA
    data.set_index(pd.to_datetime(data['date']),inplace=True)
    data.dropna(inplace=True)
    
    fig,axes = plt.subplots(3, 1, sharex = True, figsize = (17,6))
    data['close'].plot(ax = axes[0], sharex = True, color = 'b')
    axes[0].grid(True)
    axes[0].set_ylabel('Close')
    axes[0].set_title(code)
    
    axes[1].bar(data.index, data.volume/10000, color = 'r')
    axes[1].set_ylabel('volume(wan)')
    
    data[['DIFF','DEA']].plot(ax = axes[2], sharex = True)
    axes[2].set_ylabel('MACD')
    axes[2].grid(True)
    axes[2].legend(loc = 'best')
    plt.subplots_adjust(hspace = 0.1)
    
    plt.plot()
    plt.show()

if __name__ == '__main__':
    plotStock('600837', '2015-01-01', '2017-03-31')