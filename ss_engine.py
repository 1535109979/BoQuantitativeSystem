import logging
import os
import sqlite3

import pandas as pd

from BoQuantitativeSystem.backtest.read_db import ReadDB
from BoQuantitativeSystem.config.config import Configs
from BoQuantitativeSystem.do.portfolio_process import PortfolioProcess
from BoQuantitativeSystem.market.ms_grpc_stub import MarketStub
from BoQuantitativeSystem.trade.td_gateway import TDGateway


class SsEngine:
    def __init__(self):
        self.engine_mode = Configs.engine_mode
        self.account_type = Configs.account_type

        self.portfolio_maps = {}
        self.td_gateway = None
        self.ms_stub = None
        self.logger = None
        self.create_logger()

        self.quote_data = []

    def start(self):
        if self.engine_mode == 'backtest':
            self.load_data()
            self.run_backtest()

        elif self.engine_mode == 'trade':
            self.ms_stub = MarketStub()
            self.td_gateway = TDGateway(self)
            self.load_portfolio_config()
            # MarketStub().subscribe_stream_in_new_thread(instruments=['rb2509'], on_quote=self.on_quote)
            # MarketStub().subscribe_stream_in_new_thread(instruments=['ONDOUSDT'], on_quote=self.on_quote)
            MarketStub().subscribe_stream_in_new_thread(instruments=self.portfolio_maps.keys(), on_quote=self.on_quote)
            self.logger.info(f'subscribe instruments={self.portfolio_maps.keys()}')




    def load_portfolio_config(self):
        # 加载策略配置
        for instrument_config in Configs.instrument_configs:
            instrument_config.update(Configs.base_config)

            self.portfolio_maps[instrument_config['instrument']] = PortfolioProcess(self, instrument_config)
            self.logger.info(f'<load_portfolio_config> {instrument_config}')

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
        # print(quote)
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

