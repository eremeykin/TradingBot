from builtins import range
import requests
import time
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


    def get_candles(self):
        try:
            print("set connection")
            s = requests.Session()
            headers = {'Authorization': 'Bearer ' + self.token,
                       # 'X-Accept-Datetime-Format' : 'unix'
            }
            params = {'instrument': self.instrument, 'count': 20,
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
            print("make order")
            s = requests.Session()
            s.keep_alive = False
            headers = {'Authorization': 'Bearer ' + self.token,
                       'X-Accept-Datetime-Format': 'unix',
                       'Connection': 'close',
                       'Client-Identificator': str(self.id),
                       "Content-Type": 'application/x-www-form-urlencoded'
            }

            params = urllib.parse.urlencode({
                "instrument": self.instrument,
                "units": units,
                "type": 'market',  # now!
                "side": side,  # "buy" price-up ("sell"  price-down)
                "takeProfit": take_profit,
                "stopLoss": stop_loss
            })
            req = requests.post(self.order_url, data=params, headers=headers)
            for line in req.iter_lines(1):
                print("order resp: ", line)
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
                    candles = self.get_candles()
                    msg = json.loads(candles.text)
                    last_complete_candle = msg['candles'][0]
                    values = []
                    for candle in msg['candles']:
                        date = date2num(datetime.strptime(candle['time'],'%Y-%m-%dT%H:%M:%S.%fZ'))
                        openBid = float(candle['openBid'])
                        closeBid = float(candle['closeBid'])
                        highBid = float(candle['highBid'])
                        lowBid = float(candle['lowBid'])
                        value = (date,openBid,closeBid,highBid,lowBid)
                        values.append(value)

                    self.plot.update(values,clear=True)
                    # print(tick)
                print(line)

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
