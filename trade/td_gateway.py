import logging
import time
from copy import copy
from datetime import datetime
from decimal import Decimal

from BoQuantitativeSystem.config.config import Configs
from BoQuantitativeSystem.trade.bian_future_api import BiFutureTd
from BoQuantitativeSystem.utils.dingding import Dingding
from BoQuantitativeSystem.utils.exchange_enum import ExchangeType


class TDGateway:
    def __init__(self, ss_gateway):
        self.logger = ss_gateway.logger
        self.client = None
        self.account_book = None

        self.connect()

    def connect(self):

        if Configs.account_type == 'CRYPTO':
            self.client = BiFutureTd(self)
            self.client.connect()
            self.account_book = self.client.account_book


    def get_api_configs(self):
        return Configs.crypto_setting

    def send_position_error_msg(self, instrument, error):
        self.logger.error(f"<send_position_error_msg> {instrument} {error}")
        self.send_msg(f"<send_position_error_msg> {instrument} {error}")

    def send_start_unsuccessful_msg(self, msg):
        self.logger.error(f"<send_start_unsuccessful_msg> {msg}")
        self.send_msg(f"<send_start_unsuccessful_msg> {msg}")

    def send_start_msg(self, login_reqid):
        self.logger.info(f"<send_start_msg> {login_reqid}")
        self.send_msg(f"<send_start_msg> td {login_reqid}")

    def on_front_disconnected(self, msg):
        self.logger.info(f"<on_front_disconnected> {msg}")
        self.send_msg(msg)

    def gen_error_order_id(self, err_msg):
        self.send_msg(err_msg)

    @property
    def exchange_type(self):
        return ExchangeType.BINANCE_F

    def send_msg(self, msg):
        # Dingding.send_msg(msg)
        pass
