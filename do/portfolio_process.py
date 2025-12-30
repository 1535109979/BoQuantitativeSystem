import json
import logging
import os
import time
from datetime import datetime, timedelta

import pandas

from BoQuantitativeSystem.config.config import Configs
from BoQuantitativeSystem.strategys.bid import BidStrategy
from BoQuantitativeSystem.strategys.breakout import BreakoutStrategy
from BoQuantitativeSystem.strategys.change_rate_diff import ChangeRateDiffStrategy
from BoQuantitativeSystem.strategys.stop_loss import StopLoss
from BoQuantitativeSystem.utils.sys_exception import common_exception


class PortfolioProcess:

    def __init__(self, engine, instrument_config):
        self.engine = engine
        self.params = instrument_config
        self.create_logger()
        self.strategy_list = []
        self.latest_price_list = []
        self.df_data = {}

        self.load_strategy()

    def update_param(self, params):
        self.params = params
        self.get_klines()
        self.logger.info(f'<PortfolioProcess update_param> params={params}')
        self.td_gateway.send_msg(f'PortfolioProcess update_param: params={params}')

    @common_exception(log_flag=True)
    def on_quote(self, quote):
        # print('quote', quote['symbol'], quote)
        # print('on_quote', self.params)
        # print(self.td_gateway)
        # return
        self.logger.info(f"{quote['symbol']} {self.params}")
        if self.params['status'] == 'ENABLE':
            for strategy in self.strategy_list:
                strategy.cal_indicator(quote)

            for strategy in self.strategy_list:
                strategy.cal_singal(quote)

    def load_strategy(self):
        if 'breakout' in self.params['strategy_name']:
            self.get_klines(2100, self.params['instrument'])
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

        if 'rate_diff' in self.params['strategy_name']:
            b = ChangeRateDiffStrategy(self, self.params)
            self.strategy_list.append(b)
            self.logger.info(f'<load_strategy>: rate_diff params={self.params}')

    def get_klines(self, min_save_window=2100, symbol='BTCUSDT'):
        st_time = int(time.time()) - min_save_window * 60
        end_time = int(time.time())
        self.download_data(st_time, end_time, symbol, "1m")

    @common_exception(log_flag=True)
    def download_data(self, start_time, end_time, symbol='BTCUSDT', interval='1m'):
        st_time = start_time
        df_list = []
        while st_time < end_time:
            df = self.get_future_data(st_time, symbol, interval)
            df['close'] = df['close'].astype(float)
            df['symbol'] = symbol
            df_list.append(df)
            self.latest_price_list += df['close'].to_list()
            st_time = st_time + 1000 * 60

        self.df_data.update({symbol:pandas.concat(df_list, ignore_index=True)})
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
        os.makedirs(Configs.root_fp + f'logs/{self.engine.account_id}', exist_ok=True)

        self.logger = logging.getLogger(f'strategy_{self.params["instrument"]}')
        self.logger.setLevel(logging.DEBUG)
        log_fp = Configs.root_fp + f'logs/{self.engine.account_id}/{self.params["instrument"]}.log'

        from logging.handlers import TimedRotatingFileHandler
        handler = TimedRotatingFileHandler(log_fp, when="midnight", interval=1, backupCount=7)
        handler.suffix = "%Y-%m-%d.log"  # 设置滚动后文件的后缀
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - PID:%(process)d - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    @property
    def td_gateway(self):
        return self.engine.td_gateway