from binance.spot import Spot
from BoQuantitativeSystem.config.config import Configs

setting = Configs.get_setting('bo')

api_key=setting.get('api_key')
secret_key=setting.get('secret_key')

client = Spot(api_key=api_key, api_secret=secret_key,timeout=5)


res = client.get_orders(symbol='BNBUSDT', orderId='5448501041', limit=1)

print(res)


