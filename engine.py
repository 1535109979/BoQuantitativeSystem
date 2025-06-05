import logging
import sqlite3

import pandas as pd

from BoQuantitativeSystem.config.config import Configs
from BoQuantitativeSystem.do.portfolio_process import PortfolioProcess


class Engine:
    def __init__(self, engine_mode='backtest',source_type = 'CRYPTO', settle_mode='trade_settle', start_time = '2025-01-01 00:00:00'):
        self.engine_mode = engine_mode
        self.source_type = source_type
        self.daily_settlement = settle_mode
        self.start_time = start_time
        self.portfolio_maps = {}

        self.quote_data = []

    def start(self):
        self.load_portfolio_config()

        if self.engine_mode == 'backtest':
            self.read_db()
            self.run_backtest()

    def load_portfolio_config(self):
        # 加载策略配置
        for instrument_config in Configs.instrument_configs:
            instrument_config.update(Configs.base_config)

            self.portfolio_maps[instrument_config['instrument']] = PortfolioProcess(self, instrument_config)

    def read_db(self):
        if self.source_type == 'CRYPTO':
            for symbol, _ in self.portfolio_maps.items():
                print(f'-----开始加载 {symbol} 行情数据-----')
                with sqlite3.connect(Configs.db_fp) as conn:
                    df = pd.read_sql(
                        f'select * from future_{symbol} where start_time >= "{self.start_time}" order by start_time DESC',
                        conn)

                    df = df.sort_values(by='start_time').reset_index(drop=True)
                    df['symbol'] = symbol
                self.quote_data.extend([row.to_dict() for index, row in df.iterrows()])
                print(f'-----加载 {symbol} 行情成功，共{len(df)}条数据 -----')
                self.quote_data.sort(key=lambda x: x['start_time'])

    def run_backtest(self):
        if self.quote_data:
            for quote in self.quote_data:
                self.on_quote(quote)

    def on_quote(self, quote):
        quote = {k: str(v) for k, v in quote.items() if v is not None}
        instrument = quote['symbol']
        p = self.portfolio_maps.get(instrument)
        if p:
            p.on_quote(quote)


