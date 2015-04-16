import pandas as pd
import numpy as np
from datetime import *
import dateutil.parser

def conv_str_to_datetime(x):
	return dateutil.parser.parse(x)

df = pd.read_csv('tick data/EUR_USD_Week1*.csv', names=['lTid', 'cDealable', 'CurrencyPair', 'RateDateTime','RateBid','RateAsk'], converters={'RateDateTime': conv_str_to_datetime}, index_col='RateDateTime')

grouped = df.groupby('CurrencyPair')
ask =  grouped['RateAsk'].resample('15Min', how='ohlc')
bid = grouped['RateBid'].resample('15Min', how='ohlc')
res = pd.concat([ask, bid], axis=1, keys=['RateAsk', 'RateBid'])
print(res)