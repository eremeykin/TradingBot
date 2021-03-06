from builtins import range
import requests
import time
import json
import urllib.parse
import matplotlib.pyplot as plt
import datetime
from matplotlib.pyplot import subplots, draw
from matplotlib.finance import candlestick, candlestick2
from datetime import datetime
from matplotlib.dates import date2num
from matplotlib import dates
from test_bot1 import ServerConnection
import dateutil.parser
from TickRepository import TickRepository
from pprint import pprint

class ServerConnection2(ServerConnection):
    """Печать тиков с построением свечей."""


    def __init__(self):   
        self.c=0
        plt.ion()
        self.plot = Candleplot()
        self.tr=TickRepository()

    # We'll fire you if you override this method.
    def process_tick(self,msg):
        tick = {
            'time': dateutil.parser.parse(msg['tick']['time']),
            'ask': msg['tick']['ask'],
            'bid': msg['tick']['bid']
        }
        ask=float(msg['tick']['ask'])
        bid=float(msg['tick']['bid'])
        # print(tick)
        # self.c+=1
        # print('Принято '+str(self.c)+' тиков.')
        # Если минута не изменилась
        # то просто добавляем тик и уходим
        if len(self.tr.ticks)>0 and self.tr.ticks[-1]['time'].minute==tick['time'].minute:
            self.tr.add(tick)
            return
        self.tr.add(tick)
        # обработка ситуации на рынке
        #  анализ по ask
        candles = self.tr.get_candles(4)
        msg = json.loads(candles)
        if len(msg['candles'])<4:
            return
        if self.try_long(msg['candles']):
            self.plot.save(msg)
            self.order('EUR_USD', 100, 'buy', ask+0.0007, bid-0.0004)
        elif self.try_short(msg['candles']):    
            self.plot.save(msg)
            self.order('EUR_USD', 100, 'sell', ask-0.0004, bid+0.0007)


    def process_heartbeat(self,msg):
        return


    def check_candle(self,candle):
        return True
        # если было слишком мало тиков в свече,
        # то по ней прогноз не делаем
        if candle['volume']<1:
            # print('мало тиков')
            return False
        # если тело свечи маленькое,
        # то по ней прогноз не делаем
        if abs((candle['closeAsk']-candle['openAsk'])/(candle['lowAsk']-candle['highAsk']))<0.4:
            # print('маленькое тело')
            return False
        # если свеча не полная,
        # то по ней прогноз не делаем
        if candle['complete']=='False':
            # print('не полная')
            return False
        return True
    

    def is_bear(self,candle):
        # print ("проверка is_bear:")
        # print(candle)
        # print(candle['closeAsk']<candle['openAsk'])
        return candle['closeAsk']<candle['openAsk']


    def is_bull(self,candle):
        # print ("проверка is_bull:")
        # print(candle)
        # print(candle['closeAsk']>candle['openAsk'])
        return candle['closeAsk']>candle['openAsk']


    def try_long(self,candles):
        for c in candles[0:3]:
            if not self.check_candle(c):
                return False
            if not self.is_bear(c):
                return False
        if self.is_bull(candles[3]) and candles[3]['closeAsk']>candles[2]['openAsk']:
            # print("\a\nORDER\n")
            # print(candles)
            return True


    def try_short(self,candles):
        for c in candles[0:3]:
            if not self.check_candle(c):
                return False
            if not self.is_bull(c):
                return False
        if self.is_bear(candles[3]) and candles[3]['closeAsk']<candles[2]['openAsk']:
            # print("\a\nORDER\n")
            # print(candles)
            return True


class Candleplot():

    counter=0
    
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(bottom=0.2)
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
        # plt.draw()


    def save(self,msg):
        self.counter+=1
        values = []
        for candle in msg['candles']:
            date = date2num(datetime.strptime(candle['time'],'%Y-%m-%dT%H:%M:%S.%fZ'))
            openBid = candle['openAsk']
            closeBid = candle['closeAsk']
            highBid = candle['highAsk']
            lowBid = candle['lowAsk']
            value = (date,openBid,closeBid,highBid,lowBid)
            values.append(value)
        self.update(values,clear=True)
        self.fig.savefig('orders/order#'+str(self.counter)+'(ask).png')
        f=open('orders/order#'+str(self.counter)+'.ord','w')
        pprint(msg, f)

if __name__ == "__main__":
    ServerConnection2().start()
