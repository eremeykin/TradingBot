from builtins import range
import requests
import time
import json
import urllib.parse
import threading
import matplotlib.pyplot as plt
from optparse import OptionParser
import datetime


class ServerConnection(object):
    """Простая печать тиков."""

    accountId = "5968094"
    token = '645ed9d76182140938834f0c240a9ac6-b088512f8d506024c55dd72d24423efb'
    url = "https://stream-fxpractice.oanda.com/v1/prices"
    order_url = "https://" + "api-fxpractice.oanda.com" + "/v1/accounts/" + accountId + "/orders"
    candles_url = "https://api-fxpractice.oanda.com/v1/candles"
    instrument = "EUR_USD"
    time_out = 2000

    def connect_to_stream(self):
        try:
            print("set connection")
            s = requests.Session()
            headers = {'Authorization': 'Bearer ' + self.token}
            params = {'instruments': self.instrument, 'accountId': self.accountId}
            req = requests.Request('GET', self.url, headers=headers, params=params)
            pre = req.prepare()
            resp = s.send(pre, stream=True, verify=False, timeout=self.time_out)
            return resp
        except Exception as e:
            print("Caught exception when connecting to stream. Exception message:\n" + str(e))
            s.close()
            exit()


    def order(self, instr, units, side, take_profit, stop_loss):
        try:
            print("make order\a")
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
        if not response or response.status_code != 200:
            print('not response or !=200')
            return
        self.process_response(response)
        

    def process_response(self,response):
        for line in response.iter_lines(1):
            if line:
                try:
                    line = line.decode('utf-8')
                    msg = json.loads(line)
                except Exception as e:
                    print("Caught exception when converting message into json. Exception message:\n" + str(e))
                    return
                if 'tick' in msg:
                    self.process_tick(msg)
                elif 'heartbeat' in msg:
                    self.process_heartbeat(msg)
                else: 
                    raise


    def process_tick(self,msg):
        tick = {
            'time': msg['tick']['time'],
            'ask': msg['tick']['bid'],
            'bid': msg['tick']['ask']
        }
        print(msg)

    def process_heartbeat(self,msg):
        print(msg)

if __name__ == "__main__":
    ServerConnection().start()
