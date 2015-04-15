import json
from dateutil import parser
import matplotlib.pyplot as plt
import numpy as np


item='ask' # метка 'ask' или 'bid'
data_file = open('tick data/tick_Data1.txt', 'r') # файл с историческими данными
# инициализация первых значений
first_values=[]
for i in range(0,2):
	line = data_file.readline()
	msg = json.loads(line)
	value = msg['tick'][item]
	t = parser.parse(msg['tick']['time'])
	first_values.append({'value':value,'time':t})
if first_values[0]['value']<first_values[1]['value']:
	curr_trend = 'UP'
elif first_values[0]['value']>first_values[1]['value']:
	curr_trend = 'DOWN'
else:
	curr_trend = 'NONE'

curr_value = first_values[1]['value']
curr_time = first_values[1]['time']
start_value = first_values[0]['value']
start_time = first_values[0]['time']

# список трендов, т.е. кортежей (<тип>,<H>,<L>)
# <тип> = UP/DOWN/NONE
# <H> - высота 
# <L> - длина в секундах
trends=[]
count=0 # счтечик

# прогон по всему файлу
for line in data_file:
	msg = json.loads(line)
	# установка значений
	prev_value = curr_value
	curr_value = msg['tick'][item]
	prev_time = curr_time
	curr_time = parser.parse(msg['tick']['time'])
	# установка трендов
	prev_trend = curr_trend
	if curr_value>prev_value:
		prev_trend = curr_trend
		curr_trend = 'UP'
	elif curr_value<prev_value:
		prev_trend = curr_trend
		curr_trend = 'DOWN'
	else:
		prev_trend = curr_trend
		curr_trend = 'NONE'
	# если тренд изменился, записываем предыдущий в список
	if curr_trend!=prev_trend:
		d_value = prev_value-start_value
		d_time = (prev_time-start_time).total_seconds()
		trends.append((prev_trend,d_value,d_time))
		start_value = prev_value
		start_time = prev_time
	count+=1
	if count>10:
		break
print(trends)
up_trends = [x[2] for x in trends if x[0]=='UP' and x[2]<30]

hist, bins = np.histogram(up_trends, bins=10)
width = 0.7 * (bins[1] - bins[0])
center = (bins[:-1] + bins[1:]) / 2
plt.bar(center, hist, align='center', width=width)
plt.show()
