import json
import time
from dataclasses import asdict
from datetime import date, datetime

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
        self.stop_profit_decline_rate = param_json['stop_profit_decline_rate']

        self.symbol1, self.symbol2 = param_json['symbol_pair'].split('_')
        self.today = date.today()
        self.base_price = {}
        self.latest_price_map = {}
        self.change_rate = {}
        self.signal = None
        self.trading_flag = None
        self.df_s1_today = None
        self.df_s2_today = None
        self.daily_open_flag = None
        self.max_profit_rate = 0
        self.load_data()

    def update_param(self):
        self.load_data()
        self.params = self.strategy_process.params
        self.logger.info(f'ChangeRateDiffStrategy: params={self.params}')

    def load_data(self):
        self.strategy_process.get_klines(60*24, self.symbol1)
        self.strategy_process.get_klines(60*24, self.symbol2)

        today = date.today()
        df_s1 = self.strategy_process.df_data.get(self.symbol1)
        df_s2 = self.strategy_process.df_data.get(self.symbol2)
        self.df_s1_today = df_s1.loc[df_s1['start_time'].dt.date == today]
        self.df_s2_today = df_s2.loc[df_s1['start_time'].dt.date == today]

        if self.df_s1_today.empty or self.df_s2_today.empty:
            return
        self.base_price[self.symbol1] = float(self.df_s1_today['open'].iloc[0])
        self.base_price[self.symbol2] = float(self.df_s2_today['open'].iloc[0])

    @common_exception(log_flag=True)
    def cal_indicator(self, quote):
        last_price = float(quote['last_price'])
        instrument = quote['symbol']
        self.latest_price_map[instrument] = last_price

        self.signal = None

        today = date.today()
        if not today == self.today:
            self.today = today
            self.load_data()
            self.logger.info('change date')
            return

        if not self.base_price.get(instrument):
            self.logger.info(f'not base price {instrument}')
            self.load_data()
            return

        now = datetime.now()
        if (now.hour == 0) and (now.minute < 5):
            return

        elif (now.hour == 0) and (now.minute == 5):
            self.load_data()
            self.logger.info('change date')


        rate = last_price / self.base_price[instrument] - 1
        self.change_rate[instrument] = round(rate, 8)
        if self.change_rate.get(self.symbol1) and self.change_rate.get(self.symbol2):
            change_diff = (self.change_rate[self.symbol1] - self.change_rate[self.symbol2]) * 100
            self.logger.info(f'base price: {self.base_price} change rate: {self.change_rate} change_diff: {change_diff}')

            if change_diff > self.open_rate:
                self.signal = [Direction.LONG,change_diff]
            elif change_diff < -self.open_rate:
                self.signal = [Direction.SHORT,change_diff]
        else:
            self.logger.info(f'loss change_rate base_price:{self.base_price} change_rate:{self.change_rate}')

    @common_exception(log_flag=True)
    def cal_singal(self, quote):

        if self.trading_flag:
            if time.time() - self.trading_flag < 3:
                self.logger.info(f'filter by trading flag')
                return

        s1_position_long = self.strategy_process.td_gateway.account_book.get_instrument_position(
            f'{self.symbol1}.{self.strategy_process.td_gateway.exchange_type}', Direction.LONG)
        s1_position_short= self.strategy_process.td_gateway.account_book.get_instrument_position(
            f'{self.symbol1}.{self.strategy_process.td_gateway.exchange_type}',Direction.SHORT)
        s2_position_long = self.strategy_process.td_gateway.account_book.get_instrument_position(
            f'{self.symbol2}.{self.strategy_process.td_gateway.exchange_type}', Direction.LONG)
        s2_position_short = self.strategy_process.td_gateway.account_book.get_instrument_position(
            f'{self.symbol2}.{self.strategy_process.td_gateway.exchange_type}', Direction.SHORT)

        cash = self.params['cash']
        price_s1 = self.latest_price_map.get(self.symbol1)
        price_s2 = self.latest_price_map.get(self.symbol2)
        if price_s1 is None or price_s2 is None:
            self.logger.info(f'less latest price {self.latest_price_map}')
            return

        if s1_position_long.volume:
            s1_position_long.update_pnl(self.latest_price_map.get(self.symbol1))
        if s1_position_short.volume:
            s1_position_short.update_pnl(self.latest_price_map.get(self.symbol1))
        if s2_position_long.volume:
            s2_position_long.update_pnl(self.latest_price_map.get(self.symbol2))
        if s2_position_short.volume:
            s2_position_short.update_pnl(self.latest_price_map.get(self.symbol2))

        self.logger.info(f's1 long:{s1_position_long} s1 short{s1_position_short} '
                         f's2 long:{s2_position_long} s2 short{s2_position_short} ')
        self.logger.info(f's1 long:volume={s1_position_long.volume} pnl={s1_position_long.pnl} ,'
                         f's1 short:volume={s1_position_short.volume} pnl={s1_position_short.pnl}, '
                         f's2 long:volume={s2_position_long.volume} pnl={s2_position_long.pnl} ,'
                         f's2 short:volume={s2_position_short.volume}  pnl:{s2_position_short.pnl}')

        if s1_position_long.volume or s2_position_long.volume:
            profit = s1_position_long.pnl + s2_position_long.pnl + s1_position_short.pnl + s2_position_short.pnl
            profit_rate = (profit / cash) * 100

            if profit_rate > self.max_profit_rate:
                self.max_profit_rate = profit_rate

            self.logger.info(f'max_profit_rate:{self.max_profit_rate} now profit_rate:{profit_rate}')

            if profit_rate <= self.max_profit_rate - self.stop_profit_decline_rate:
                if s1_position_long.volume:
                    self.logger.info(f'close symbol1 long symbol2 short '
                                     f'max_profit_rate={self.max_profit_rate} now_profit_rate={profit_rate}')
                    self.strategy_process.td_gateway.insert_order(self.symbol1, OffsetFlag.CLOSE,
                        Direction.LONG,OrderPriceType.LIMIT, str(price_s1),s1_position_long.volume)
                    self.strategy_process.td_gateway.insert_order(self.symbol2, OffsetFlag.CLOSE,
                        Direction.SHORT, OrderPriceType.LIMIT, str(price_s2),s2_position_short.volume)

                    self.trading_flag = time.time()
                    self.max_profit_rate = 0
                    self.daily_open_flag = date.today()

                if s2_position_long.volume:
                    self.logger.info(f'close symbol2 long symbol1 short '
                                     f'max_profit_rate={self.max_profit_rate} now_profit_rate={profit_rate}')
                    self.strategy_process.td_gateway.insert_order(self.symbol1, OffsetFlag.CLOSE,
                         Direction.SHORT, OrderPriceType.LIMIT, str(price_s1),s1_position_short.volume)
                    self.strategy_process.td_gateway.insert_order(self.symbol2, OffsetFlag.CLOSE,
                         Direction.LONG, OrderPriceType.LIMIT,str(price_s2), s2_position_long.volume)

                    self.trading_flag = time.time()
                    self.max_profit_rate = 0
                    self.daily_open_flag = date.today()
        else:
            self.max_profit_rate = 0
            if self.signal:

                if self.daily_open_flag:
                    if self.daily_open_flag == date.today():
                        self.logger.info('skip by daily open')
                        return

                signal_dir = self.signal[0]

                if signal_dir == Direction.LONG and s1_position_long.volume:
                    self.logger.info(f'holding {signal_dir}')
                    return
                elif signal_dir == Direction.SHORT and s2_position_long.volume:
                    self.logger.info(f'holding {signal_dir}')
                    return

                self.strategy_process.td_gateway.insert_order(self.symbol1, OffsetFlag.OPEN,
                                signal_dir, OrderPriceType.LIMIT, str(price_s1), cash=self.params['cash'])
                self.strategy_process.td_gateway.insert_order(self.symbol2, OffsetFlag.OPEN,
                                signal_dir.get_opposite_direction(), OrderPriceType.LIMIT, str(price_s2),
                                                              cash=self.params['cash'])
                self.logger.info(f'open {signal_dir} diff:{self.signal[1]} {self.symbol1} {self.symbol2}')
                self.trading_flag = time.time()
                self.daily_open_flag = date.today()
                self.signal = None

