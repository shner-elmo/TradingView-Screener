from tv_scanner import TradingViewScanner
from time import sleep
from datetime import *
import pytz


def time(hour: int, minute: int, second: int = 0, microsecond: int = 0):
    """return time object, requires hour and minute parameters, optional params: second and microsecond"""
    today = datetime.now(tz=pytz.timezone('US/Eastern'))
    return datetime(today.year, today.month, today.day, hour=hour,
                    minute=minute, second=second, microsecond=microsecond)


tvs = TradingViewScanner()
my_list = []
my_dict = {}

while True:
    current_time = datetime.now(tz=pytz.timezone('US/Eastern'))
    time_obj = time(9, 8)  # time of the test: 09:08 est time

    if current_time.hour == time_obj.hour and current_time.minute == time_obj.minute:
        for i in range(50):
            data = tvs.get_data(scanner_type='pm_gainers', return_type='dict')
            top_symbol = list(sorted(data, key=lambda x: data[x]['premarket_volume'], reverse=True))[0]

            top_volume = data[top_symbol]['premarket_volume']
            my_list.append(top_volume)
            sleep(10)
        break

print('list =', my_list)

# I did two tests; one on my PC, and the other on my Laptop (both on the same wifi connection)
# they were both run at exactly the same time,
# and as we can see from the output, the values are nearly identical and get updated once per minute weather
# we provide cookies or not. (even if your account is pro and has NYSE and NASDAQ data add-ons)
# So no, it doesn't really matter if you provide cookies or not.

# output with cookies:
'''list = [14998949, 15083294, 15083294, 15083294, 15083294, 15083294, 15087408, 15087408, 15087408, 15087408, 15087408, 15087408, 15087408, 15230750, 15230750, 15230750, 15230750, 15230750, 15284264, 15284264, 15284264, 15284264, 15284264, 15308423, 15308423, 15308423, 15308423, 15308423, 15308423, 15328811, 15328811, 15328811, 15328811, 15328811, 15328811, 15343816, 15343816, 15343816, 15343816, 15343816, 15343816, 15356446, 15356446, 15356446, 15356446, 15356446, 15356446, 15424188, 15424188, 15424188]'''
# output without:
'''list = [14998949, 15083294, 15083294, 15083294, 15083294, 15083294, 15087408, 15087408, 15087408, 15087408, 15087408, 15087408, 15230750, 15230750, 15230750, 15230750, 15230750, 15230750, 15284264, 15284264, 15284264, 15284264, 15284264, 15308423, 15308423, 15308423, 15308423, 15308423, 15308423, 15328811, 15328811, 15328811, 15328811, 15328811, 15328811, 15343816, 15343816, 15343816, 15343816, 15343816, 15343816, 15356446, 15356446, 15356446, 15356446, 15356446, 15356446, 15424188, 15424188, 15424188]'''
