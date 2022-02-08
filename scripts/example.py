import pandas as pd
from matplotlib import pyplot as plt

from data.nasdaqdatahandler import NasdaqDataHandler


ndx_handler = NasdaqDataHandler("CHRIS/ICE_KC1")
# print(ndx_handler.get_table_name())
# print(ndx_handler.get_local_filename())
# ndx_handler.clear()
# data_orig = ndx_handler.obtain()
data = ndx_handler.get()
data['date'] = pd.to_datetime(data.date)
data = data[data.date.dt.year > 2018]
pd.set_option('display.max_columns', None)
print(data.columns.values)
print(data.head())

data.plot(x='date', y='settle', figsize=(10, 5))
plt.show()
