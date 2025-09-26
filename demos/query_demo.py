import json
import logging

import pandas as pd
import requests
from binance.um_futures import UMFutures


# HMAC authentication with API key and secret
key = "b9b98tFEOvo4hdRKkblM33l5hf8WAg99l4SS3aOGNsDKH8yOJ8cXu08JBIfE9BmJ"
secret = "1PYXKw57m7DtjFj4moeRtYlCSHwazR7NSyv75ysPeIxBcTfYcuFUdjc5f3B8Z8rR"

hmac_client = UMFutures(key=key, secret=secret)
# da = hmac_client.query('/futures/data/openInterestHist')
# print(da)

# res = hmac_client.account(recvWindow=6000)
# print(res.keys())
# print(res['positions'])
# for s in res['assets']:
#     print(s)

# ex = hmac_client.exchange_info()
# print(ex)
# symbols = ex['symbols']
# print(symbols[0])
# #
# print(len(symbols))
#
# df = pd.DataFrame(symbols)
# print(df)

import requests

base_url = 'https://fapi.binance.com'          # 1. 去掉空格
endpoint = '/futures/data/openInterestHist'
params = {                                     # 2. 用 params
    'symbol': 'BTCUSDT',
    'period': '1h',                            # 3. 加上周期
    'limit': 1                                # 可选：最近 30 条
}

r = requests.get(base_url + endpoint, params=params)
r.raise_for_status()
print(r.json())        # 列表，每条含 timestamp / openInterest / sumOpenInterest