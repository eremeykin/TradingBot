# TradingBot

Простой пробный бот. Выводит в режиме реального времени ask и bid для EUR/USD. <I>(Примечание: по выходным торги закрыты)</I>

# Установка

Модуль requests для запросов на сервер. Используя pip:

    $ sudo pip3 install requests

Модуль matplotlib для построения графика:

    $ sudo pip3 install matplotlib

Модуль Pyke: 
Скачать с [sourceforge](http://sourceforge.net/projects/pyke/files/pyke/1.1.1/pyke3-1.1.1.zip/download), распаковать. Выполнить из директории с файлами: 

    $ python3 setup.py build
    $ sudo python3 setup.py install

Проверка:

    $ python3 
    >>> from pyke import knowledge_engine
    
# Запуск

    $ python3 test_bot1.py
    
# Пример вывода 

set connection
[{'time': '2015-03-19T16:36:22.286105Z', 'bid': 1.06378, 'ask': 1.06391}]
{"tick":{"instrument":"EUR_USD","time":"2015-03-19T16:36:22.286105Z","bid":1.06378,"ask":1.06391}}
{"heartbeat":{"time":"2015-03-19T16:36:26.028119Z"}}
{"heartbeat":{"time":"2015-03-19T16:36:28.457620Z"}}
