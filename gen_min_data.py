import pandas as pd
import numpy as np
from datetime import *
import dateutil.parser
import json
'''Генерирует файл с минутными данными в json'''

def conv_str_to_datetime(x):
    return dateutil.parser.parse(x)

df = pd.read_csv('tick data/EUR_USD_Week1*.csv', names=['lTid', 'cDealable', 'CurrencyPair', 'RateDateTime','RateBid','RateAsk'], converters={'RateDateTime': conv_str_to_datetime}, index_col='RateDateTime')

grouped = df.groupby('CurrencyPair')
ask =  grouped['RateAsk'].resample('1Min', how='ohlc')
bid = grouped['RateBid'].resample('1Min', how='ohlc')
res = pd.concat([ask, bid], axis=1, keys=['RateAsk', 'RateBid'])
f1=open('tick data/Week1_1min.json', 'w+')

count = 0
for index, row in res.iterrows():
    time = index[1].isoformat()+".000000Z"
    openBid = row['RateBid']['open']
    openAsk = row['RateAsk']['open']
    highBid = row['RateBid']['high']
    highAsk = row['RateAsk']['high']
    lowBid = row['RateBid']['low']
    lowAsk = row['RateAsk']['open']
    closeBid = row['RateBid']['close']
    closeAsk = row['RateAsk']['close']
    volume = 0,
    complete = 'true'
    line =      {
        "time" : time,
        "openBid" :  round(openBid,5),
        "openAsk" :  round(openAsk,5),
        "highBid" :  round(highBid,5),
        "highAsk" :  round(highAsk,5),
        "lowBid"  :  round(lowBid,5),
        "lowAsk"  :  round(lowAsk,5),
        "closeBid" : round(closeBid,5),
        "closeAsk" : round(closeAsk,5),
        "volume" : 0,
        "complete" : True
    }
    string = json.dumps(line, ensure_ascii=False)
    count+=1
    # line = '{\"tick\":{\"instrument\":\"EUR_TSD\",\"time\":\"'+time+'\",\"bid\":'+bid+',\"ask\":'+ask+'}}'
    if not 'nan' in line.values():
        f1.write(string+"\r\n")
print(ask)