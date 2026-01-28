
import json
import time
from dataclasses import asdict
from datetime import date, datetime

from BoQuantitativeSystem.database.use_data import UseInstrumentConfig
from BoQuantitativeSystem.utils.aio_timer import AioTimer
from BoQuantitativeSystem.utils.exchange_enum import Direction, OffsetFlag, OrderPriceType
from BoQuantitativeSystem.utils.sys_exception import common_exception


class ChangeRateDiffStrategy():
    def __init__(self, strategy_process, params):
        self.strategy_process = strategy_process
        self.logger = self.strategy_process.logger

        self.params = params
        self.instrument = params['instrument']
        self.symbol1, self.symbol2 = params['instrument'].split('_')
        self.open_rate = params['open_rate']
        self.win_stop_profit_rate = params['win_stop_profit_rate']
        self.loss_stop_profit_rate = params['loss_stop_profit_rate']
        self.max_profit_rate = params['max_profit_rate']
        self.daily_trade_flag = params['daily_trade_flag']

        param_json = eval(params['param_json'])
        self.position_flag = param_json.get('position_flag')
        self.s1_open_price = param_json.get('s1_open_price')
        self.s2_open_price = param_json.get('s2_open_price')

        self.today = date.today()
        self.base_price = {}
        self.latest_price_map = {}
        self.change_rate = {}
        self.signal = None
        self.trading_flag = None
        self.df_s1_today = None
        self.df_s2_today = None
        self.update_data_flag = False
        self.profit_rate = 0

        self.load_data()

        self._save_profit_rate_timer(interval=60)

    @common_exception(log_flag=True)
    def cal_indicator(self, quote):
        last_price = float(quote['last_price'])
        instrument = quote['symbol']
        self.latest_price_map[instrument] = last_price
        now = datetime.now()
        today = date.today()

        self.signal = None

        if not today == self.today:
            self.today = today
            self.update_data_flag = False
            self.logger.info('need change date')
            return

        if (now.hour == 0) and (now.minute == 5) and not self.update_data_flag:
            self.load_data()
            self.logger.info('change date')

        if not self.base_price.get(instrument):
            self.logger.info(f'not base price {instrument}')
            self.load_data()
            return

        rate = last_price / self.base_price[instrument] - 1
        self.change_rate[instrument] = round(rate, 8)
        if self.change_rate.get(self.symbol1) and self.change_rate.get(self.symbol2):
            change_diff = (self.change_rate[self.symbol1] - self.change_rate[self.symbol2]) * 100

            if change_diff > self.open_rate:
                self.signal = Direction.LONG
            elif change_diff < -self.open_rate:
                self.signal = Direction.SHORT

            self.logger.info(f'base price: {self.base_price} latest_price_map:{self.latest_price_map} '
                             f'change rate: {self.change_rate} change_diff: {change_diff} '
                             f'signal:{self.signal} position_flag:{self.position_flag} '
                             f'daily_trade_flag:{self.daily_trade_flag}')
        else:
            self.logger.info(f'loss change_rate base_price:{self.base_price} change_rate:{self.change_rate}')

        if (now.hour == 0) and (now.minute < 10):
            self.logger.info('skip by time')
            self.signal = None

    @common_exception(log_flag=True)
    def cal_singal(self, quote):

        if self.trading_flag:
            if time.time() - self.trading_flag < 3:
                self.logger.info(f'filter by trading flag')
                return

        cash = self.params['cash']
        price_s1 = self.latest_price_map.get(self.symbol1)
        price_s2 = self.latest_price_map.get(self.symbol2)

        s1_position_long = self.strategy_process.td_gateway.account_book.get_instrument_position(
            f'{self.symbol1}.{self.strategy_process.td_gateway.exchange_type}', Direction.LONG)
        s1_position_short = self.strategy_process.td_gateway.account_book.get_instrument_position(
            f'{self.symbol1}.{self.strategy_process.td_gateway.exchange_type}', Direction.SHORT)
        s2_position_long = self.strategy_process.td_gateway.account_book.get_instrument_position(
            f'{self.symbol2}.{self.strategy_process.td_gateway.exchange_type}', Direction.LONG)
        s2_position_short = self.strategy_process.td_gateway.account_book.get_instrument_position(
            f'{self.symbol2}.{self.strategy_process.td_gateway.exchange_type}', Direction.SHORT)

        self.logger.info(f'{self.symbol1} long:{s1_position_long}')
        self.logger.info(f'{self.symbol1} short:{s1_position_short}')
        self.logger.info(f'{self.symbol2} long:{s2_position_long}')
        self.logger.info(f'{self.symbol2} short:{s2_position_short}')

        if self.position_flag:
            if self.position_flag == 1:
                s1_profit_rate = (price_s1 / self.s1_open_price - 1)  * 100
                s2_profit_rate = - (price_s2 / self.s2_open_price - 1) * 100
                self.profit_rate = s1_profit_rate + s2_profit_rate
            elif self.position_flag == -1:
                s1_profit_rate = -(price_s1 / self.s1_open_price - 1) * 100
                s2_profit_rate = (price_s2 / self.s2_open_price - 1) * 100
                self.profit_rate = s1_profit_rate + s2_profit_rate

            if self.profit_rate > self.max_profit_rate:
                self.max_profit_rate = self.profit_rate
                self.logger.info(f'update and save max profit rate: {self.max_profit_rate}')
                self.save_max_profit_rate(self.max_profit_rate)
            self.logger.info(f'max_profit_rate:{self.max_profit_rate} now profit_rate:{self.profit_rate}')

            close_flag = False

            if self.profit_rate > 0:
                if self.profit_rate <= self.max_profit_rate - self.win_stop_profit_rate:
                    close_flag = True
                    self.logger.info(f'close by win profit_rate={self.profit_rate}')
            else:
                if self.profit_rate <= self.max_profit_rate - self.loss_stop_profit_rate:
                    close_flag = True
                    self.logger.info(f'close by loss profit_rate={self.profit_rate}')

            if close_flag:
                if self.position_flag == 1:
                    self.logger.info(f'insert order close symbol1 long symbol2 short')

                    if s1_position_long.volume * self.latest_price_map.get(self.symbol1) > cash * 1.5:
                        self.strategy_process.td_gateway.insert_order(self.symbol1, OffsetFlag.CLOSE,
                              Direction.LONG, OrderPriceType.LIMIT,str(price_s1),s1_position_long.volume, cash=cash)
                    else:
                        self.strategy_process.td_gateway.insert_order(self.symbol1, OffsetFlag.CLOSE,
                              Direction.LONG, OrderPriceType.LIMIT,str(price_s1),s1_position_long.volume)

                    if s2_position_short.volume * self.latest_price_map.get(self.symbol2) > cash * 1.5:
                        self.strategy_process.td_gateway.insert_order(self.symbol2, OffsetFlag.CLOSE,
                             Direction.SHORT, OrderPriceType.LIMIT,str(price_s2),s2_position_short.volume, cash=cash)
                    else:
                        self.strategy_process.td_gateway.insert_order(self.symbol2, OffsetFlag.CLOSE,
                             Direction.SHORT, OrderPriceType.LIMIT,str(price_s2),s2_position_short.volume)

                elif self.position_flag == -1:
                    self.logger.info(f'insert order close symbol2 long symbol1 short')
                    if s2_position_long * self.latest_price_map.get(self.symbol2) > cash * 1.5:
                        self.strategy_process.td_gateway.insert_order(self.symbol2, OffsetFlag.CLOSE,
                            Direction.LONG, OrderPriceType.LIMIT,str(price_s1), s2_position_long.volume, cash=cash)
                    else:
                        self.strategy_process.td_gateway.insert_order(self.symbol2, OffsetFlag.CLOSE,
                             Direction.LONG, OrderPriceType.LIMIT,str(price_s1), s2_position_long.volume)

                    if s1_position_short.volume * self.latest_price_map.get(self.symbol1) > cash * 1.5:
                        self.strategy_process.td_gateway.insert_order(self.symbol1, OffsetFlag.CLOSE,
                             Direction.SHORT, OrderPriceType.LIMIT,str(price_s2), s1_position_short.volume,cash=cash)
                    else:
                        self.strategy_process.td_gateway.insert_order(self.symbol1, OffsetFlag.CLOSE,
                             Direction.SHORT, OrderPriceType.LIMIT,str(price_s2), s1_position_short.volume)

                self.save_position({'position_flag': 0, 's1_open_price': 0, 's2_open_price': 0})
                self.save_daily_trade_flag()
                self.max_profit_rate = 0
                self.save_max_profit_rate(0)
        else:
            if self.max_profit_rate or self.profit_rate:
                self.logger.error(f'data error position_flag:{self.position_flag} '
                                  f'max_profit_rate: {self.max_profit_rate} profit_rate: {self.profit_rate}')
                return

            if self.signal:
                if self.daily_trade_flag:
                    if self.daily_trade_flag == date.today():
                        self.logger.info('skip by daily open')
                        return

                self.logger.info(f'insert order open {self.signal} {self.symbol1} {self.symbol2}')
                self.strategy_process.td_gateway.insert_order(self.symbol1, OffsetFlag.OPEN,
                     self.signal, OrderPriceType.LIMIT, str(price_s1), cash=self.params['cash'])
                self.strategy_process.td_gateway.insert_order(self.symbol2, OffsetFlag.OPEN,
                      self.signal.get_opposite_direction(), OrderPriceType.LIMIT,str(price_s2),cash=self.params['cash'])

                self.save_position({'position_flag': self.signal.value,
                                    's1_open_price': price_s1,
                                    's2_open_price': price_s2})
                self.trading_flag = time.time()
                self.save_daily_trade_flag()
                self.signal = None

    def _save_profit_rate_timer(self, interval):
        def _func():
            self._save_profit_rate_timer(interval)

            self.save_profit_rate()

        AioTimer.new_timer(_delay=interval, _func=_func)

    def save_daily_trade_flag(self):
        self.daily_trade_flag = date.today()
        self.logger.info(f'save daily_trade_flag={self.daily_trade_flag}')
        update_date = UseInstrumentConfig.get(UseInstrumentConfig.instrument == self.instrument)
        update_date.daily_trade_flag = self.daily_trade_flag
        update_date.save()

    def save_max_profit_rate(self, max_profit_rate):
        update_date = UseInstrumentConfig.get(UseInstrumentConfig.instrument == self.instrument)
        update_date.max_profit_rate = max_profit_rate
        update_date.save()

    def save_profit_rate(self):
        update_date = UseInstrumentConfig.get(UseInstrumentConfig.instrument == self.instrument)
        update_date.stop_profit_rate = round(self.profit_rate ,2)
        update_date.save()

    def save_position(self, param_json):
        self.position_flag = param_json['position_flag']
        self.s1_open_price = param_json['s1_open_price']
        self.s2_open_price = param_json['s2_open_price']

        update_date = UseInstrumentConfig.get(UseInstrumentConfig.instrument == self.instrument)
        update_date.param_json = param_json
        update_date.save()

    def update_param(self):
        self.load_data()
        self.params = self.strategy_process.params
        self.logger.info(f'ChangeRateDiffStrategy: params={self.params}')

    def load_data(self):
        self.strategy_process.get_klines(60 *24, self.symbol1)
        self.strategy_process.get_klines(60 *24, self.symbol2)

        today = date.today()
        df_s1 = self.strategy_process.df_data.get(self.symbol1)
        df_s2 = self.strategy_process.df_data.get(self.symbol2)
        self.df_s1_today = df_s1.loc[df_s1['start_time'].dt.date == today]
        self.df_s2_today = df_s2.loc[df_s2['start_time'].dt.date == today]

        if self.df_s1_today.empty or self.df_s2_today.empty:
            return
        self.base_price[self.symbol1] = float(self.df_s1_today['open'].iloc[0])
        self.base_price[self.symbol2] = float(self.df_s2_today['open'].iloc[0])

        self.update_data_flag = True

