from builtins import range
import requests
import time
import json
import urllib.parse
import threading
import matplotlib.pyplot as plt
from optparse import OptionParser
import datetime


class ServerConnection(threading.Thread):
    """ServerConnection"""

    accountId = "5968094"
    token = '645ed9d76182140938834f0c240a9ac6-b088512f8d506024c55dd72d24423efb'
    url = "https://stream-fxpractice.oanda.com/v1/prices"
    order_url = "https://" + "api-fxpractice.oanda.com" + "/v1/accounts/" + accountId + "/orders"
    instrument = "EUR_USD"
    test_mode = True
    displayHeartbeat = False
    tick_event = threading.Event()
    time_out = 2000
    start = False
    ticks = list()


    def __init__(self, test_mode):
        # self.resp = self.connect_to_stream()
        self.test_mode=test_mode
        if test_mode:
            # self.url = "http://127.0.0.1:8080"
            # self.order_url = "http://127.0.0.1:8080"
            self.url = "http://192.168.1.191:8080"
            self.order_url = "http://192.168.1.191:8080"

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
            if self.test_mode:
                self.id = int(resp.headers['client-identificator'])
                print(str(self.id))
            else:
                self.id = 0
            return resp
        except Exception as e:
            print("Caught exception when connecting to stream. Exception message:\n" + str(e))
            s.close()

    def _get_next(self, id):
        if self.test_mode:
            try:
                s = requests.Session()
                headers = {'Action': 'need_next_tick',
                           'Client-Identificator': str(self.id)
                }
                # params = {'action' : 'getnext' + str(count)}
                req = requests.Request('GET', self.url, headers=headers)
                pre = req.prepare()
                resp = s.send(pre, stream=False, verify=False, timeout=self.time_out)
                return resp
            except Exception as e:
                print("Caught exception when connecting to stream. Exception message:\n" + str(e))
                s.close()
        else:
            return

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
        plt.plot(self.ticks)
        plt.ion()
        plt.show()
        start = True
        response = self.connect_to_stream()
        tick = {
            'time': 0,
            'ask': 0,
            'bid': 0
        }
        dec = 0
        inc = 0
        if not response:
            return
        if response.status_code != 200:
            return
        try:
            self._get_next(0)
            for line in response.iter_lines(1):

                if line:
                    try:
                        line = line.decode('utf-8')
                        msg = json.loads(line)
                    except Exception as e:
                        print("Caught exception when converting message into json. Exception message:\n" + str(e))
                        return

                    # if '\"bid\":1.2472,' in line:
                    # print("O_R_D_E_R")
                    # self.order(instr=self.instrument, units=10, side='sell', take_profit=1.2470, stop_loss=1.2475)
                    if 'tick' in msg:
                        time = msg['tick']['time']
                        ask = msg['tick']['ask']
                        bid = msg['tick']['bid']
                        if tick['ask'] - ask > 0:
                            dec = 0
                            inc += 1
                        elif tick['bid'] - bid < 0:
                            inc = 0
                            dec += 1
                        else:
                            inc = 0
                            dec = 0
                        if dec > 5:
                            self.order(instr=self.instrument, units=10, side='buy', take_profit=ask * 1.002,
                                       stop_loss=ask * 0.998)
                            print('Order buy')
                        if inc > 5:
                            self.order(instr=self.instrument, units=10, side='sell', take_profit=ask * 0.998,
                                       stop_loss=ask * 1.002)
                            print('Order sell')
                        tick = {
                            'time': time,
                            'ask': ask,
                            'bid': bid
                        }
                        self.ticks.append(tick)
                        print(self.ticks)
                    print(line)
                    x = [item['ask'] for item in self.ticks]

                    plt.clf()
                    if len(x) > 40:
                        plt.plot(x[len(x) - 40:])
                    plt.draw()
                self._get_next(0)


        except Exception as e:
            print("Caught exception when reading response. Exception message:\n" + str(e))


if __name__ == "__main__":
    sc = ServerConnection(test_mode=False)
    # sc.order(instr = sc.instrument,units=10,side='buy',take_profit='1000',stop_loss='1.24680')
    sc.start()