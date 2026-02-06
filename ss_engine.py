import importlib
import os
from multiprocessing import Process

from BoQuantitativeSystem.database.use_data import UseInstrumentConfig

import json
import logging
import os
import sqlite3
import threading
import time

import pandas as pd
from dataclasses import dataclass, field, asdict
from typing import Dict
from multiprocessing import Process


import redis
from binance.um_futures import UMFutures

from BoQuantitativeSystem.config.config import Configs
from BoQuantitativeSystem.database.use_data import UseInstrumentConfig
from BoQuantitativeSystem.do.portfolio_process import PortfolioProcess
from BoQuantitativeSystem.market.ms_grpc_stub import MarketStub
from BoQuantitativeSystem.strategys.books.use_instrument_config import UseInstrumentConfigBook
from BoQuantitativeSystem.trade.td_gateway import TDGateway
from BoQuantitativeSystem.utils.aio_timer import AioTimer
from BoQuantitativeSystem.utils.dingding import Dingding
from BoQuantitativeSystem.utils.sys_exception import common_exception

class SsEngine:
    def __init__(self, account_id):
        self.account_id = account_id
        self.engine_mode = Configs.engine_mode
        self.account_type = Configs.account_type
        self.use_instrument_config: Dict[str, Dict[str, UseInstrumentConfigBook]] = {}
        self.portfolio_maps = {}
        self.instrument_quote_time_map = {}
        self.td_gateway = None
        self.ms_stub = None
        self.logger = None
        self.create_logger()

        self.quote_data = []
        self.r = redis.Redis(**Configs.redis_setting)
        self.redis_client = self.r.pubsub()
        self.sub_redis_thread = threading.Thread(target=self.subscribe_redis)

        self._check_quote_timer(interval=40)

    def _check_quote_timer(self, interval):
        def _func():
            self._check_quote_timer(interval)

            self._check_quote_time()

        AioTimer.new_timer(_delay=interval, _func=_func)

    def subscribe_redis(self):
        # 循环监听消息
        for message in self.redis_client.listen():
            # 调用消息处理函数处理接收到的消息
            self.handle_redis_message(message)

    @common_exception(log_flag=True)
    def handle_redis_message(self, message):
        self.logger.info(f'<handle_redis_message> message={message}')
        if message['type'] == 'message':

            message = json.loads(message['data'])
            instrument = message['instrument']
            p_list = self.portfolio_maps.get(message['instrument'])
            if p_list:
                for p in p_list:
                    p.update_param(message)
                self.logger.info(f'update_param {instrument}:{message}')
            else:
                self.portfolio_maps[message['instrument']] = PortfolioProcess(self, message)
                self.ms_stub.subscribe_stream_in_new_thread(instruments=[instrument], on_quote=self.on_quote)
                self.logger.info(f'<handle_redis_message> add instruments={message}')

    def start(self):
            self.kline_client = UMFutures()
            self.ms_stub = MarketStub()
            self.load_portfolio_config()

            self.sub_redis_thread.start()

            self.td_gateway = TDGateway(self, self.account_id)

            # # MarketStub().subscribe_stream_in_new_thread(instruments=['rb2509'], on_quote=self.on_quote)
            # # MarketStub().subscribe_stream_in_new_thread(instruments=['ONDOUSDT'], on_quote=self.on_quote)
            self.ms_stub.subscribe_stream_in_new_thread(instruments=self.portfolio_maps.keys(), on_quote=self.on_quote)
            # self.ms_stub.subscribe_stream_in_new_thread(instruments=['BNBUSDT'], on_quote=self.on_quote)
            self.logger.info(f'subscribe instruments={self.portfolio_maps.keys()}')

    @common_exception(log_flag=True)
    def load_portfolio_config(self):
        print(self.account_id, os.getpid())
        rows = UseInstrumentConfig.select().where(UseInstrumentConfig.account_id == self.account_id)
        self.use_instrument_config[self.account_id] = {str(r.instrument).upper():UseInstrumentConfigBook.create_by_row(r)
                                                  for r in rows}
        self.redis_client.subscribe(self.account_id)

        for account_id, use_instrument_config_books in self.use_instrument_config.items():
            for instrument, instrument_config in use_instrument_config_books.items():
                instrument_config = asdict(instrument_config)
                if instrument_config['status'] == 'ENABLE':
                    if 'rate_diff' in instrument_config['strategy_name']:
                        s1, s2 = instrument_config["instrument"].split('_')
                        self.ms_stub.subscribe_stream_in_new_thread(instruments=[s1, s2], on_quote=self.on_quote)
                        p = PortfolioProcess(self, instrument_config)
                        # self.portfolio_maps[s1] = p
                        # self.portfolio_maps[s2] = p
                        self.portfolio_maps[instrument] = [p]
                        if self.portfolio_maps.get(s1):
                            self.portfolio_maps[s1].append(p)
                        else:
                            self.portfolio_maps[s1] = [p]

                        if self.portfolio_maps.get(s2):
                            self.portfolio_maps[s2].append(p)
                        else:
                            self.portfolio_maps[s2] = [p]

                    else:
                        self.portfolio_maps[instrument] = PortfolioProcess(self, instrument_config)
        print(self.portfolio_maps)

    def _check_quote_time(self):
        for instrument, quote in self.instrument_quote_time_map.items():
            now_t = time.time()
            t = float(quote.get('ms_gateway_timestamp'))
            if now_t - t > 180:
                Dingding.send_msg(f'miss quote {instrument}')

    def on_quote(self, quote):
        if not self.td_gateway:
            return

        quote = {k: str(v) for k, v in quote.items() if v is not None}
        # print(time.time())
        # print(os.getpid(), self.account_id, self.td_gateway.account_book.balance, 'quote', quote['symbol'], quote)
        # return
        instrument = quote['symbol']

        self.instrument_quote_time_map.update({instrument: quote})

        p_list = self.portfolio_maps.get(instrument)
        if p_list:
            for p in p_list:
                p.on_quote(quote)
        else:
            self.logger.info(f'not portfolio {instrument}', quote)

    def create_logger(self):
        self.logger = logging.getLogger('bi_future_ss')
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        self.logger.handlers = []

        os.makedirs(Configs.root_fp + f'logs', exist_ok=True)
        log_fp = Configs.root_fp + f'logs/{self.account_id}_bi_future_ss.log'

        from logging.handlers import TimedRotatingFileHandler
        handler = TimedRotatingFileHandler(log_fp, when="midnight", interval=1, backupCount=2)
        handler.suffix = "%Y-%m-%d.log"  # 设置滚动后文件的后缀
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - PID:%(process)d - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


def run_engine(acc):
    SsEngine(acc).start()

    while 1:
        pass

if __name__ == '__main__':
    account_ids = [row.account_id for row in
                   UseInstrumentConfig.select(UseInstrumentConfig.account_id).distinct()]

    for account_id in account_ids:
        p = Process(target=run_engine,args=(account_id,), daemon=True)
        p.start()

    # Process(target=run_engine, args=('bo',), daemon=True).start()

    # SsEngine('feng').start()

    while 1:
        pass

