import json
import time
from dataclasses import asdict
from datetime import date

from BoQuantitativeSystem.utils.exchange_enum import Direction, OffsetFlag, OrderPriceType
from BoQuantitativeSystem.utils.sys_exception import common_exception


class ChangeRateDiffStrategy():
    def __init__(self, strategy_process, params):
        self.strategy_process = strategy_process
        self.logger = self.strategy_process.logger

        self.params = params
        param_json = eval(params['param_json'])
        self.open_rate = param_json['open_rate']
        self.close_rate = param_json['close_rate']
        self.symbol1, self.symbol2 = param_json['symbol_pair'].split('_')
        self.today = date.today()
        self.base_price = {}
        self.change_rate = {}
        self.singal_dir = None
        self.trading_flag = None
        self.max_profit_rate = 0
        self.load_data()

    def update_param(self):
        self.load_data()
        self.logger.info(f'ChangeRateDiffStrategy: params={self.params}')

    def load_data(self):
        self.strategy_process.get_klines(60*24, self.symbol1)
        self.strategy_process.get_klines(60*24, self.symbol2)

        today = date.today()
        df_s1 = self.strategy_process.df_data.get(self.symbol1)
        df_s2 = self.strategy_process.df_data.get(self.symbol2)
        self.base_price[self.symbol1] = [float(df_s1.loc[df_s1['start_time'].dt.date == today, 'open'].iloc[0]), 1]
        self.base_price[self.symbol2] = [float(df_s2.loc[df_s2['start_time'].dt.date == today, 'open'].iloc[0]), 1]

    @common_exception(log_flag=True)
    def cal_indicator(self, quote):
        last_price = float(quote['last_price'])
        instrument = quote['symbol']

        today = date.today()
        if not today == self.today:
            self.today = today
            self.base_price[self.symbol1][1] = 0
            self.base_price[self.symbol2][1] = 0
            self.load_data()
            self.logger.info('change date')
            return True

        if not self.base_price[instrument][1]:
            self.logger.info(f'not update base price success')
            return

        rate = last_price / self.base_price[instrument][0] - 1
        self.change_rate[instrument] = round(rate, 8)
        if self.change_rate.get(self.symbol1) and self.change_rate.get(self.symbol2):
            change_diff = (self.change_rate[self.symbol1] - self.change_rate[self.symbol2]) * 100
            self.logger.info(f'base price: {self.base_price} change rate: {self.change_rate} change_diff: {change_diff}')
            if change_diff > self.open_rate:
                self.singal_dir = Direction.LONG
            elif change_diff < -self.open_rate:
                self.singal_dir = Direction.SHORT
        else:
            self.logger.info(f'base_price:{self.base_price} change_rate:{self.change_rate}')

    @common_exception(log_flag=True)
    def cal_singal(self, quote):
        last_price = float(quote['last_price'])

        if self.trading_flag:
            if time.time() - self.trading_flag < 30:
                self.logger.info(f'filter by trading flag')
                return
        return
        s1_position_long = self.strategy_process.td_gateway.account_book.get_instrument_position(
            f'{self.symbol1}.{self.strategy_process.td_gateway.exchange_type}', Direction.LONG)
        s1_position_short= self.strategy_process.td_gateway.account_book.get_instrument_position(
            f'{self.symbol1}.{self.strategy_process.td_gateway.exchange_type}',Direction.SHORT)
        s2_position_long = self.strategy_process.td_gateway.account_book.get_instrument_position(
            f'{self.symbol2}.{self.strategy_process.td_gateway.exchange_type}', Direction.LONG)
        s2_position_short = self.strategy_process.td_gateway.account_book.get_instrument_position(
            f'{self.symbol2}.{self.strategy_process.td_gateway.exchange_type}', Direction.SHORT)

        self.logger.info(f's1 long pnl:{s1_position_long.pnl} ,s1 short pnl:{s1_position_short.pnl}, '
                         f's2 long pnl:{s2_position_long.pnl} ,s2 short pnl:{s2_position_short.pnl}')

        if s1_position_long.volume or s2_position_long.volume:
            cash = self.params['cash']
            profit = s1_position_long.pnl + s2_position_long.pnl + s1_position_short.pnl + s2_position_short.pnl
            profit_rate = profit / cash

            if profit_rate > self.max_profit_rate:
                self.max_profit_rate = profit_rate

            self.logger.info(f'max_profit_rate:{self.max_profit_rate} now profit_rate:{profit_rate}')

            if profit_rate <= self.max_profit_rate - 0.3:
                if s1_position_long.volume:
                    self.strategy_process.td_gateway.insert_order(self.symbol1, OffsetFlag.CLOSE,
                        Direction.LONG,OrderPriceType.LIMIT, str(last_price),s1_position_long.volume)
                    self.strategy_process.td_gateway.insert_order(self.symbol2, OffsetFlag.CLOSE,
                        Direction.SHORT, OrderPriceType.LIMIT, str(last_price),s2_position_short.volume)
                    self.logger.info('close symbol1 long symbol2 short')
                    self.trading_flag = time.time()
                if s2_position_long.volume:
                    self.strategy_process.td_gateway.insert_order(self.symbol1, OffsetFlag.CLOSE,
                         Direction.SHORT, OrderPriceType.LIMIT, str(last_price),s1_position_short.volume)
                    self.strategy_process.td_gateway.insert_order(self.symbol2, OffsetFlag.CLOSE,
                         Direction.LONG, OrderPriceType.LIMIT,str(last_price), s2_position_long.volume)
                    self.logger.info('close symbol2 long symbol1 short')
                    self.trading_flag = time.time()

        else:
            if self.singal_dir:
                self.strategy_process.td_gateway.insert_order(self.symbol1, OffsetFlag.OPEN,
                                self.singal_dir, OrderPriceType.LIMIT, str(last_price), cash=self.params['cash'])
                self.strategy_process.td_gateway.insert_order(self.symbol2, OffsetFlag.OPEN,
                                self.singal_dir.get_opposite_direction(), OrderPriceType.LIMIT, str(last_price),
                                                              cash=self.params['cash'])
                self.logger.info(f'open {self.singal_dir}')
                self.trading_flag = time.time()




