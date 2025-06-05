import logging

from BoQuantitativeSystem.config.config import Configs
from BoQuantitativeSystem.strategys.bid import BidStrategy
from BoQuantitativeSystem.strategys.breakout import BreakoutStrategy


class PortfolioProcess:

    def __init__(self, engine, instrument_config):
        self.engine = engine
        self.td_gateway = self.engine.td_gateway
        self.params = instrument_config
        self.create_logger()
        self.strategy_list = []

        self.load_strategy()

    def on_quote(self, quote):
        print(quote)
        print(self.params)
        quit()

    def load_strategy(self):
        if 'breakout' in self.params['strategy_name']:
            b = BreakoutStrategy(self, self.params)
            self.strategy_list.append(b)

        if 'bid' in self.params['strategy_name']:
            b = BidStrategy(self, self.params)
            self.strategy_list.append(b)

    def create_logger(self):
        self.logger = logging.getLogger(f'strategy_{self.params["instrument"]}')
        self.logger.setLevel(logging.DEBUG)
        log_fp = Configs.root_fp + f'BoQuantitativeSystem/logs/strategy_logs/{self.params["instrument"]}.log'

        from logging.handlers import TimedRotatingFileHandler
        handler = TimedRotatingFileHandler(log_fp, when="midnight", interval=1, backupCount=7)
        handler.suffix = "%Y-%m-%d.log"  # 设置滚动后文件的后缀
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
