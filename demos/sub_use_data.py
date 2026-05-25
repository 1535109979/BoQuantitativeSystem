import time
import logging
from binance.lib.utils import config_logging
from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

from BoQuantitativeSystem.config.config import Configs


def message_handler(_, message):
    print(message)


configs = Configs.get_setting('bo')
client =UMFutures(key=configs["api_key"], secret=configs["secret_key"],
                         base_url='https://fapi.binance.com')
response = client.new_listen_key()

logging.info("Listen key : {}".format(response["listenKey"]))

ws_client = UMFuturesWebsocketClient(stream_url='wss://fstream.binance.com/private',on_message=message_handler)

ws_client.user_data(
    listen_key=response["listenKey"],
    id=1,
)


time.sleep(500)


