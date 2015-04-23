import dateutil.parser
import json
import pandas as pd
from pprint import pprint


class TickRepository():

    # по умолчанию вместимость 1200 сек, интервал 60 сек
    def __init__(self, capacity=1200, interval=60):
        self.capacity = capacity
        self.interval = interval
        self.ticks=[]


    # добавляет тик в хранилище
    # тик требуется в виде словаря, причем поле 'time' должно быть datetime
    def add(self, curr_tick):
        self.curr_tick=curr_tick
        self.ticks.append(curr_tick)
        tick=self.ticks[0]
        sec = (curr_tick['time'].replace(second=0,microsecond=0)-tick['time']).total_seconds()
        if sec<-self.interval or sec>self.capacity:
            self.ticks.remove(tick)       


    # возвращает тики, которые отстаят от текущего не более чем на 
    # count интервалов (например, минут), начиная с последней закрытой минуты,
    # т.е. если время 16:23:35 то тики начинаются с 16:22:59 и меньше
    def get_last(self, count):
        aux=[]
        for tick in self.ticks:
            sec = (self.curr_tick['time'].replace(second=0,microsecond=0)-tick['time']).total_seconds()
            if sec>0 and sec< self.interval*count:
                aux.append(tick)
        return aux



    def get_candles(self, count):
        c=self.get_last(count)
        frame = pd.DataFrame(c)
        if frame.empty:
            return json.dumps({'candles':[]}, ensure_ascii=False)
        frame =frame.set_index(pd.DatetimeIndex(frame['time']))
        ask = frame['ask'].resample('1Min', how='ohlc')
        bid = frame['bid'].resample('1Min', how='ohlc')
        common = pd.concat([ask, bid], axis=1, keys=['ask', 'bid'])
        result={'candles':[]}
        for index, row in common.iterrows():
            time = index.isoformat()+".000000Z"
            openBid = row['bid']['open']
            openAsk = row['ask']['open']
            highBid = row['bid']['high']
            highAsk = row['ask']['high']
            lowBid = row['bid']['low']
            lowAsk = row['ask']['open']
            closeBid = row['bid']['close']
            closeAsk = row['ask']['close']
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
            result['candles'].append(line)
        result['candles'].sort(key=self.getKey,reverse=False)
        return json.dumps(result, ensure_ascii=False)

    def getKey(self,item):
        return item['time']