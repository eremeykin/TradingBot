from builtins import range
import requests
import time
import json
import urllib.parse
import matplotlib.pyplot as plt
import datetime
import matplotlib.pyplot as plt
from matplotlib.pyplot import subplots, draw
from matplotlib.finance import candlestick, candlestick2
from datetime import datetime
from matplotlib.dates import date2num
from time import sleep
from matplotlib import dates
from test_bot1 import ServerConnection

class ServerConnection2(ServerConnection):
    """Печать тиков с построением свечей."""


    def __init__(self):   
        plt.ion()
        self.plot = Candleplot()


    def get_candles(self,count):
        try:
            # print("get candles")
            s = requests.Session()
            headers = {'Authorization': 'Bearer ' + self.token,
                       'Client-Identificator':str(self.accountId)
            }
            params = {'instrument': self.instrument, 'count': count,'granularity':'M1'}
            url = self.candles_url
            req = requests.Request('GET', url, headers=headers, params=params)
            pre = req.prepare()
            resp = s.send(pre, stream=False, verify=False, timeout=self.time_out)
            return resp
        except Exception as e:
            print("Caught exception when connecting to stream. Exception message:\n" + str(e))
            s.close()


    def process_tick(self,msg):

        tick = {
            'time': msg['tick']['time'],
            'ask': msg['tick']['bid'],
            'bid': msg['tick']['ask']
        }
        candles = self.get_candles(20)
        try:
            msg = json.loads(candles.text)
        except Exception as e:
            print("Caught exception when parsing json. Exception message:\n" + str(e))

        last_complete_candle = msg['candles'][0]
        values = []
        for candle in msg['candles']:
            date = date2num(datetime.strptime(candle['time'],'%Y-%m-%dT%H:%M:%S.%fZ'))
            openBid = candle['openBid']
            closeBid = candle['closeBid']
            highBid = candle['highBid']
            lowBid = candle['lowBid']
            value = (date,openBid,closeBid,highBid,lowBid)
            values.append(value)

        self.plot.update(values,clear=True)
        candles = self.get_candles(5)
        msg = json.loads(candles.text)
        # if self.try_long(msg['candles']):
        #     self.order('EUR_USD', 100, 'buy', ask+0.0007, bid-0.0004)
        #     t.sleep(60) # Заменить НЕМЕДЛЕННО
        # elif self.try_short(msg['candles']):    
        #     self.order('EUR_USD', 100, 'sell', ask-0.0004, bid+0.0007)
        #     t.sleep(60) # Заменить НЕМЕДЛЕННО
        
        candles = self.get_candles(15)
        msg = json.loads(candles.text)


    def process_heartbeat(self,msg):
        candles = self.get_candles(20)
        msg = json.loads(candles.text)
        last_complete_candle = msg['candles'][0]
        values = []
        for candle in msg['candles']:
            date = date2num(datetime.strptime(candle['time'],'%Y-%m-%dT%H:%M:%S.%fZ'))
            openBid = candle['openBid']
            closeBid = candle['closeBid']
            highBid = candle['highBid']
            lowBid = candle['lowBid']
            value = (date,openBid,closeBid,highBid,lowBid)
            values.append(value)

        self.plot.update(values,clear=True)


    def check_candle(self,candle):
        return True
        # если было слишком мало тиков в свече,
        # то по ней прогноз не делаем
        if candle['volume']<1:
            print('мало тиков')
            return False
        # если тело свечи маленькое,
        # то по ней прогноз не делаем
        if abs((candle['closeAsk']-candle['openAsk'])/(candle['lowAsk']-candle['highAsk']))<0.4:
            print('маленькое тело')
            return False
        # если свеча не полная,
        # то по ней прогноз не делаем
        if candle['complete']=='False':
            print('не полная')
            return False
        return True
    

    def is_bear(self,candle):
        print ("проверка is_bear:")
        print(candle)
        print(candle['closeAsk']<candle['openAsk'])
        return candle['closeAsk']<candle['openAsk']


    def is_bull(self,candle):
        print ("проверка is_bull:")
        print(candle)
        print(candle['closeAsk']>candle['openAsk'])
        return candle['closeAsk']>candle['openAsk']


    def try_long(self,candles):
        for c in candles[0:3]:
            if not self.check_candle(c):
                return False
            if not self.is_bear(c):
                return False
        if self.is_bull(candles[3]) and candles[3]['closeAsk']>candles[2]['openAsk']:
            print("!!!!!!!!!!!!!!!!!!!ORDER!!!")
            print(candles)
            return True


    def try_short(self,candles):
        for c in candles[0:3]:
            if not self.check_candle(c):
                return False
            if not self.is_bull(c):
                return False
        if self.is_bear(candles[3]) and candles[3]['closeAsk']<candles[2]['openAsk']:
            print("!!!!!!!!!!!!!!!!!!!ORDER!!!")
            print(candles)
            return True


class Candleplot():
    
    def __init__(self):
        fig, self.ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2)
        plt.ion()

    def update(self, quotes, clear=False):

        if clear:
            # clear old data
            self.ax.cla()

        # axis formatting
        d = []
        for value in quotes:
            data = value[0]
            d.append(data)
        self.ax.set_xlim([min(d),max(d)+0.0010])

        self.ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
        # plot quotes
        candlestick(self.ax, quotes, width=0.00005)

        # more formatting
        self.ax.xaxis_date()
        self.ax.autoscale_view()
        plt.setp( plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

        plt.draw()


if __name__ == "__main__":
    ServerConnection2().start()
