import json
import logging
import os
import sqlite3
import threading

import pandas as pd
from dataclasses import dataclass, field, asdict
from typing import Dict

import redis
from binance.um_futures import UMFutures

from BoQuantitativeSystem.backtest.read_db import ReadDB
from BoQuantitativeSystem.config.config import Configs
from BoQuantitativeSystem.database.use_data import UseInstrumentConfig
from BoQuantitativeSystem.do.portfolio_process import PortfolioProcess
from BoQuantitativeSystem.market.ms_grpc_stub import MarketStub
from BoQuantitativeSystem.strategys.books.use_instrument_config import UseInstrumentConfigBook
from BoQuantitativeSystem.trade.td_gateway import TDGateway
from BoQuantitativeSystem.utils.sys_exception import common_exception


class SsEngine:
    def __init__(self):
        self.engine_mode = Configs.engine_mode
        self.account_type = Configs.account_type
        self.use_instrument_config: Dict[str, Dict[str, UseInstrumentConfigBook]] = {}
        self.portfolio_maps = {}
        self.td_gateway = None
        self.ms_stub = None
        self.logger = None
        self.create_logger()

        self.quote_data = []
        self.r = redis.Redis(**Configs.redis_setting)
        self.redis_client = self.r.pubsub()
        self.sub_redis_thread = threading.Thread(target=self.subscribe_redis)

    def subscribe_redis(self):
        # 循环监听消息
        for message in self.redis_client.listen():
            # 调用消息处理函数处理接收到的消息
            self.handle_redis_message(message)

    def handle_redis_message(self, message):
        self.logger.info(f'<handle_redis_message> message={message}')
        if message['type'] == 'message':
            message = json.loads(message['data'])
            instrument = message['instrument']
            p = self.portfolio_maps.get(message['instrument'])
            if p:
                p.update_param(message)
            else:
                self.portfolio_maps[message['instrument']] = PortfolioProcess(self, message)
                self.ms_stub.subscribe_stream_in_new_thread(instruments=[instrument], on_quote=self.on_quote)


    def start(self):
        if self.engine_mode == 'backtest':
            self.load_data()
            self.run_backtest()

        elif self.engine_mode == 'trade':
            self.kline_client = UMFutures()
            self.ms_stub = MarketStub()
            self.load_portfolio_config()
            self.sub_redis_thread.start()

            self.td_gateway = TDGateway(self)

            # # MarketStub().subscribe_stream_in_new_thread(instruments=['rb2509'], on_quote=self.on_quote)
            # # MarketStub().subscribe_stream_in_new_thread(instruments=['ONDOUSDT'], on_quote=self.on_quote)
            self.ms_stub.subscribe_stream_in_new_thread(instruments=self.portfolio_maps.keys(), on_quote=self.on_quote)
            self.logger.info(f'subscribe instruments={self.portfolio_maps.keys()}')

    @common_exception(log_flag=True)
    def load_portfolio_config(self):
        account_ids = [row.account_id for row in
                       UseInstrumentConfig.select(UseInstrumentConfig.account_id).distinct()]

        for account_id in account_ids:
            rows = UseInstrumentConfig.select().where(UseInstrumentConfig.account_id == account_id)
            self.use_instrument_config[account_id] = {str(r.instrument).upper():UseInstrumentConfigBook.create_by_row(r)
                                                      for r in rows}
            self.redis_client.subscribe(account_id)

        for account_id, use_instrument_config_books in self.use_instrument_config.items():
            for instrument, instrument_config in use_instrument_config_books.items():
                self.portfolio_maps[instrument] = PortfolioProcess(self, asdict(instrument_config))

        # quit()
        #
        # # 加载策略配置
        # for instrument_config in Configs.strategy_list:
        #
        #     self.portfolio_maps[instrument_config['instrument']] = PortfolioProcess(self, instrument_config)
        #     self.logger.info(f'<load_portfolio_config> {instrument_config}')

    def load_data(self):
        if self.account_type == 'CRYPTO':
            for symbol, _ in self.portfolio_maps.items():
                df = ReadDB.read_crypto(symbol)
                self.quote_data.extend([row.to_dict() for index, row in df.iterrows()])

                self.quote_data.sort(key=lambda x: x['start_time'])

    def run_backtest(self):
        if self.quote_data:
            for quote in self.quote_data:
                self.on_quote(quote)

    def on_quote(self, quote):
        quote = {k: str(v) for k, v in quote.items() if v is not None}
        # print('quote', quote['symbol'])
        # return
        instrument = quote['symbol']
        p = self.portfolio_maps.get(instrument)
        if p:
            p.on_quote(quote)
        else:
            self.logger.info(f'not portfolio {instrument}', quote)

    def create_logger(self):
        self.logger = logging.getLogger('bi_future_ss')
        self.logger.setLevel(logging.DEBUG)
        log_fp = Configs.root_fp + 'logs/bi_future_ss.log'

        from logging.handlers import TimedRotatingFileHandler
        handler = TimedRotatingFileHandler(log_fp, when="midnight", interval=1, backupCount=7)
        handler.suffix = "%Y-%m-%d.log"  # 设置滚动后文件的后缀
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


if __name__ == '__main__':
    SsEngine().start()

    while 1:
        pass

