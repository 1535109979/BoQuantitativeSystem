from datetime import datetime, timedelta

import pandas
import pandas as pd
from binance.um_futures import UMFutures
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 2000)

future_client = UMFutures()

symbol='ADAUSDT'

start_time = '2026-06-09 00:00:00'

st_time =  (datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')).timestamp()

data = future_client.klines(symbol, '1m', limit=1000, startTime=int(st_time) * 1000)
df = pandas.DataFrame(data)
df.columns = ['start_time', 'open', 'high', 'low', 'close', 'vol', 'end_time',
                      'quote_asset_vol', 'number_of_trade', 'base_asset_volume', 'quote_asset_volume', 'n']
df['start_time'] = df['start_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
df['end_time'] = df['end_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
print(df)

