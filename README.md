# TradingViewScanner

#### The following quick-guide will show you how to get started using the tv_scanner module

First you must import and instantiate the TradingViewScanner class
```python
from tv_scanner import TradingViewScanner
tvs = TradingViewScanner()
```

Then, to retrieve the data you must provide the scanner type, and optionally the type to return ('df' or 'dict')
```python
data = tvs.get_data(scanner_type='pm_gainers', return_type='dict')
```

Once you have the data you can use filter() to loop through it and filter down the results.  
In our case we only want stocks that have a Pre-market change above 10% and a price bigger than $3,  
and then we save the results in a list:
```python
my_filter = list(filter(lambda x: data[x]['premarket_change_perc'] > 10 and data[x]['close'] > 3, data))
```

If we have a look at the symbols this is what we get
```python
print(my_filter)
```
```
['DRTS', 'ACLX', 'RRGB', 'PMVP', 'DELL', 'DTC', 'ZS', 'ULTA']
```
-----  
Optionally, to get the names of the columns:
```python
print(tvs.columns)
```
```
['symbol', 'premarket_close', 'premarket_change', 'premarket_change_perc'...
```

And to get a list of all the scanners available:
```python
print(tvs.scanners.keys())
```
```
dict_keys(['pm_gainers', 'pm_losers', 'pm_most_active', 'pm_gappers'])
```


