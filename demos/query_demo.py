import logging

import pandas as pd
from binance.um_futures import UMFutures


# HMAC authentication with API key and secret
key = "b9b98tFEOvo4hdRKkblM33l5hf8WAg99l4SS3aOGNsDKH8yOJ8cXu08JBIfE9BmJ"
secret = "1PYXKw57m7DtjFj4moeRtYlCSHwazR7NSyv75ysPeIxBcTfYcuFUdjc5f3B8Z8rR"

hmac_client = UMFutures(key=key, secret=secret)
res = hmac_client.account(recvWindow=6000)
# print(res.keys())
# print(res['positions'])
for s in res['assets']:
    print(s)

# ex = hmac_client.exchange_info()
# symbols = ex['symbols']
#
# print(len(symbols))
#
# df = pd.DataFrame(symbols)
# print(df)


