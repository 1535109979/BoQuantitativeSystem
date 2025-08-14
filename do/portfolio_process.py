import logging
import os
import time
from datetime import datetime, timedelta

import pandas

from BoQuantitativeSystem.config.config import Configs
from BoQuantitativeSystem.strategys.bid import BidStrategy
from BoQuantitativeSystem.strategys.breakout import BreakoutStrategy
from BoQuantitativeSystem.strategys.stop_loss import StopLoss
from BoQuantitativeSystem.utils.sys_exception import common_exception


class PortfolioProcess:

    def __init__(self, engine, instrument_config):
        self.engine = engine
        self.td_gateway = self.engine.td_gateway
        self.params = instrument_config
        self.create_logger()
        self.strategy_list = []
        self.latest_price_list = []

        self.load_strategy()

    def update_param(self, params):
        self.params = params
        self.logger.info(f'<update_param> params={params}')
        self.td_gateway.send_msg(f'update_param: params={params}')

    @common_exception(log_flag=True)
    def on_quote(self, quote):
        # print('quote', quote)
        # print('on_quote', self.params)

        if self.params['status'] == 'ENABLE':
            for strategy in self.strategy_list:
                strategy.cal_indicator(quote)

            for strategy in self.strategy_list:
                strategy.cal_singal(quote)

    def load_strategy(self):
        if 'breakout' in self.params['strategy_name']:
            self.get_klines()
            b = BreakoutStrategy(self, self.params)
            self.strategy_list.append(b)
            self.logger.info(f'<load_strategy>: breakout params={self.params}')

        if 'bid' in self.params['strategy_name']:
            b = BidStrategy(self, self.params)
            self.strategy_list.append(b)
            self.logger.info(f'<load_strategy>: bid params={self.params}')

        if 'stop_loss' in self.params['strategy_name']:
            b = StopLoss(self, self.params)
            self.strategy_list.append(b)
            self.logger.info(f'<load_strategy>: stop_loss params={self.params}')

    def get_klines(self, min_save_window=2100):
        st_time = int(time.time()) - min_save_window * 60
        end_time = int(time.time())
        self.download_data(st_time, end_time, self.params['instrument'], "1m")

    @common_exception(log_flag=True)
    def download_data(self, start_time, end_time, symbol='BTCUSDT', interval='1m'):
        st_time = start_time

        while st_time < end_time:
            df = self.get_future_data(st_time, symbol, interval)
            self.latest_price_list += df['close'].astype(float).to_list()
            st_time = st_time + 1000 * 60
        self.logger.info(f'<get_future_data>: latest_time={df.loc[len(df) - 1].close_time}')

    def get_future_data(self, st_time, symbol='BTCUSDT', interval='1m'):
        data = self.engine.kline_client.klines(symbol, interval, limit=1000, startTime=int(st_time) * 1000)
        df = pandas.DataFrame(data)
        df.columns = ['start_time', 'open', 'high', 'low', 'close', 'vol', 'end_time',
                      'quote_asset_vol', 'number_of_trade', 'base_asset_volume', 'quote_asset_volume', 'n']
        df['start_time'] = df['start_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
        df['close_time'] = df['start_time'].apply(lambda x: x + timedelta(minutes=1))
        df['end_time'] = df['end_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
        df = df.sort_values(by='close_time')
        df = df[df['close_time'] <= datetime.now()]

        return df

    def create_logger(self):
        if not os.path.exists(Configs.root_fp + 'logs/strategy_logs'):
            os.makedirs(Configs.root_fp + 'logs/strategy_logs')

        self.logger = logging.getLogger(f'strategy_{self.params["instrument"]}')
        self.logger.setLevel(logging.DEBUG)
        log_fp = Configs.root_fp + f'logs/strategy_logs/{self.params["instrument"]}.log'

        from logging.handlers import TimedRotatingFileHandler
        handler = TimedRotatingFileHandler(log_fp, when="midnight", interval=1, backupCount=7)
        handler.suffix = "%Y-%m-%d.log"  # 设置滚动后文件的后缀
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
