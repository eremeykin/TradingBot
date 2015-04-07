from builtins import range
import requests
import time as t
import json
import urllib.parse
import threading
import matplotlib.pyplot as plt
from optparse import OptionParser
import datetime
import matplotlib.pyplot as plt
from matplotlib.pyplot import subplots, draw
from matplotlib.finance import candlestick, candlestick2
from datetime import datetime
from matplotlib.dates import date2num
from time import sleep
from matplotlib import dates

class ServerConnection(object):
    """Печать тиков с построением свечей."""

    accountId = "5968094"
    token = '645ed9d76182140938834f0c240a9ac6-b088512f8d506024c55dd72d24423efb'
    url = "https://stream-fxpractice.oanda.com/v1/prices"
    order_url = "https://" + "api-fxpractice.oanda.com" + "/v1/accounts/" + accountId + "/orders"
    instrument = "EUR_USD"
    displayHeartbeat = False
    time_out = 2000
    i=0


    def __init__(self):
        print(self.i)      
        plt.ion()
        self.plot = Candleplot()
        # plt.show()


    def connect_to_stream(self):
        try:
            print("set connection")
            s = requests.Session()
            headers = {'Authorization': 'Bearer ' + self.token,
                       # 'X-Accept-Datetime-Format' : 'unix'
            }
            params = {'instruments': self.instrument, 'accountId': self.accountId}
            req = requests.Request('GET', self.url, headers=headers, params=params)
            pre = req.prepare()
            resp = s.send(pre, stream=True, verify=False, timeout=self.time_out)
            return resp
        except Exception as e:
            print("Caught exception when connecting to stream. Exception message:\n" + str(e))
            s.close()


    def get_candles(self,count):
        try:
            print("set connection")
            s = requests.Session()
            headers = {'Authorization': 'Bearer ' + self.token,
                       # 'X-Accept-Datetime-Format' : 'unix'
            }
            params = {'instrument': self.instrument, 'count': count,
            'granularity':'M1'}
            url = "https://api-fxpractice.oanda.com/v1/candles"
            req = requests.Request('GET', url, headers=headers, params=params)
            pre = req.prepare()
            resp = s.send(pre, stream=False, verify=False, timeout=self.time_out)
            return resp
        except Exception as e:
            print("Caught exception when connecting to stream. Exception message:\n" + str(e))
            s.close()


    def order(self, instr, units, side, take_profit, stop_loss):
        try:
            print("ORDER")
            print('\a')
            s = requests.Session()
            s.keep_alive = False
            headers = {'Authorization': 'Bearer ' + self.token,
                       'X-Accept-Datetime-Format': 'unix',
                       'Connection': 'close',
                       'Client-Identificator': str(self.accountId),
                       'Content-Type': 'application/x-www-form-urlencoded' 
            }

            params = urllib.parse.urlencode({
                "instrument": self.instrument,
                "units": units,
                "type": 'market',  # now!
                "side": side,  # "buy" price-up ("sell"  price-down)
                "takeProfit": "%.5f" %take_profit,
                "stopLoss": "%.5f" %stop_loss,
                "trailingStop": 5
            })
            print(params)
            req = requests.post(self.order_url, data=params, headers=headers)
            for line in req.iter_lines(1):
                print(">", line)
        except Exception as e:
            print("Caught exception when connecting to orders\n" + str(e))


    def start(self):
        response = self.connect_to_stream()
        if not response:
            return
        if response.status_code != 200:
            return
        for line in response.iter_lines(1):
            if line:
                try:
                    line = line.decode('utf-8')
                    msg = json.loads(line)
                except Exception as e:
                    print("Caught exception when converting message into json. Exception message:\n" + str(e))
                    return
                if 'tick' in msg:
                    time = msg['tick']['time']
                    ask = msg['tick']['ask']
                    bid = msg['tick']['bid']
                    tick = {
                        'time': time,
                        'ask': ask,
                        'bid': bid
                    }
                    self.i=self.i+1
                    # self.plot(self.i,ask)
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
                    candles = self.get_candles(5)
                    msg = json.loads(candles.text)
                    if self.try_long(msg['candles']):
                        self.order('EUR_USD', 100, 'buy', ask+0.0007, bid-0.0004)
                        t.sleep(60)
                    if self.try_short(msg['candles']):    
                        self.order('EUR_USD', 100, 'sell', ask-0.0004, bid+0.0007)
                        t.sleep(60)
                print('.'),


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



class Candleplot:
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
        candlestick(self.ax, quotes, width=0.00025)

        # more formatting
        self.ax.xaxis_date()
        self.ax.autoscale_view()
        plt.setp( plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

        plt.draw()



            







if __name__ == "__main__":
    ServerConnection().start()
