from test_bot2reserve import ServerConnection2
from builtins import range
import requests
import time
import json
import urllib.parse
import threading
import matplotlib.pyplot as plt
from optparse import OptionParser
import datetime
import os
from TickRepository import TickRepository


class TestServerConnection2(ServerConnection2):

    url = "http://127.0.0.1:8080"
    order_url = "http://127.0.0.1:8080"
    candles_url= "http://127.0.0.1:8080/candles"
    accountId=0
    tr=TickRepository()

    def __init__(self):
        super().__init__()
        for subdir, dirs, files in os.walk('orders'):
            for file in files:
                os.remove('orders/'+file)

    def connect_to_stream(self):
        resp = super().connect_to_stream()
        try:
            self.accountId = int(resp.headers['client-identificator'])
        except Exception as e:
            print(e)
            self.accountId = 0
        print("New client. Id="+str(self.accountId))
        return resp
        
        
    def process_response(self,response):
        self.get_next()
        for line in response.iter_lines(1):
            if line:
                try:
                    line = line.decode('utf-8')
                    msg = json.loads(line)
                except Exception as e:
                    print("Caught exception when converting message into json. Exception message:\n" + str(e))
                if 'tick' in msg:
                    # print(msg)
                    self.process_tick(msg)
                    self.get_next()


    def get_next(self):        
            s = requests.Session()
            headers = {'Action': 'need_next_tick','Client-Identificator': str(self.accountId)}
            req = requests.Request('GET', self.url, headers=headers)
            pre = req.prepare()
            resp = s.send(pre, stream=False, verify=False, timeout=self.time_out)
            return resp
        

TestServerConnection2().start()
