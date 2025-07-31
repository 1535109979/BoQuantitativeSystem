import logging
import time
from copy import copy
from datetime import datetime
from decimal import Decimal

from BoQuantitativeSystem.config.config import Configs
from BoQuantitativeSystem.database.dbm import AccountValue, TradeInfo
from BoQuantitativeSystem.trade.bian_future_api import BiFutureTd
from BoQuantitativeSystem.utils.aio_timer import AioTimer
from BoQuantitativeSystem.utils.dingding import Dingding
from BoQuantitativeSystem.utils.exchange_enum import ExchangeType, OffsetFlag, Direction, OrderPriceType
from BoQuantitativeSystem.utils.sys_exception import common_exception


class TDGateway:
    def __init__(self, ss_gateway):
        self.logger = ss_gateway.logger
        self.client = None
        self.account_book = None
        self._save_account_data_timer(interval=3600)
        self.connect()

    def connect(self):

        if Configs.account_type == 'CRYPTO':
            self.client = BiFutureTd(self)
            self.client.connect()
            self.account_book = self.client.account_book

    @common_exception(log_flag=True)
    def on_query_account(self, data):
        # self.logger.info(f"<on_query_account> data={data}")
        pass

    @common_exception(log_flag=True)
    def on_account_update(self):
        self.logger.info(f"<on_account_update> balance={self.account_book.balance}")

    def cancel_cancel_all_order(self, instrument):
        self.client.cancel_all_order(instrument)

    @common_exception(log_flag=True)
    def insert_order(self, instrument: str, offset_flag: OffsetFlag, direction: Direction,
                     order_price_type: OrderPriceType, price: float, volume: float,
                     cancel_delay_seconds: int = 0, **kwargs) -> str:
        """ 向交易所报单
        做多开仓=OPEN:LONG    做空开仓=OPEN:SHORT
        做多平仓=CLOSE:LONG   做空平仓=CLOSE:SHORT
        """
        instrument_book = self.account_book.get_instrument_book(instrument + f'.{self.exchange_type}')
        min_volume_muti = int(1 / float(instrument_book.min_volume_step))
        min_price_step = instrument_book.min_price_step

        order_step_muti = 10
        for param in Configs.strategy_list:
            if instrument == param.get('instrument'):
                order_step_muti = param['order_step_muti']
        if offset_flag == OffsetFlag.OPEN:
            if direction == Direction.LONG:
                trade_price = Decimal(price) + Decimal(min_price_step) * order_step_muti
            elif direction == Direction.SHORT:
                trade_price = Decimal(price) - Decimal(min_price_step) * order_step_muti
        elif offset_flag == OffsetFlag.CLOSE:
            if direction == Direction.LONG:
                trade_price = Decimal(price) - Decimal(min_price_step) * order_step_muti
            elif direction == Direction.SHORT:
                trade_price = Decimal(price) + Decimal(min_price_step) * order_step_muti

        if 'cash' in kwargs:
            volume = kwargs['cash'] / float(price)
            volume = round(volume * min_volume_muti) / min_volume_muti
            self.logger.info(f'use cash cal vol: min_volume_muti={min_volume_muti} cash={kwargs["cash"]} '
                             f'price={trade_price} volume={volume} order_step_muti={order_step_muti}')

        req = {
            'instrument': instrument,
            'offset_flag': offset_flag,
            'direction': direction,
            'order_price_type': order_price_type,
            'price': str(trade_price),
            'volume': str(volume),
            'cancel_delay_seconds': cancel_delay_seconds,
        }
        self.logger.info(f'<insert_order> instrument={instrument} offset_flag={offset_flag} direction={direction} '
                         f'order_price_type={order_price_type} trade_price={trade_price} volume={volume}')

        client_order_id = self.client.insert_order(
            **req, **kwargs)

        return client_order_id

    @common_exception(log_flag=True)
    def save_account_value(self):
        save_data = AccountValue(
            balance=self.account_book.balance,
            position_sum_cost=self.account_book.position_sum_cost,
            position_multi=self.account_book.position_multi,
            update_time=datetime.now(),
        )
        save_data.save()

    def _save_account_data_timer(self, interval):
        def _func():
            self._save_account_data_timer(interval)

            self.save_account_value()

        AioTimer.new_timer(_delay=interval, _func=_func)

    @common_exception(log_flag=True)
    def on_order(self, rtn_order):
        pass

    @common_exception(log_flag=True)
    def on_trade(self, rtn_trade):
        self.logger.info(f'<on_trade> save trade_data={rtn_trade}')
        trade_data = TradeInfo(
            instrument = rtn_trade.instrument,
            order_id = rtn_trade.order_id,
            client_id = rtn_trade.client_id,
            offset = rtn_trade.offset_flag,
            direction = rtn_trade.direction,
            volume = rtn_trade.volume,
            price = rtn_trade.price,
            trading_day = rtn_trade.trading_day,
            trade_time = rtn_trade.trade_time,
            profit = rtn_trade.profit,
            commission = rtn_trade.commission,
            commission_asset = rtn_trade.commission_asset,
            update_time = datetime.now(),
        )
        trade_data.save()

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
        Dingding.send_msg(msg)
        # pass
