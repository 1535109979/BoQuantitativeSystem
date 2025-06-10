import sqlite3

import pandas as pd


class ReadDB:
    @classmethod
    def read_crypto(self, symbol, strat_time='2025-01-01 00:00:00'):
        print(f'-----开始加载 {symbol} 行情数据-----')
        db_fp = '/Users/edy/byt_pub/a_songbo/binance_client/backtest/binance_quote_data.db'
        with sqlite3.connect(db_fp) as conn:
            df = pd.read_sql(
                f'select * from future_{symbol} where start_time >= "{strat_time}" order by start_time DESC',
                conn)

            df = df.sort_values(by='start_time').reset_index(drop=True)
            df['symbol'] = symbol
            df['last_price'] = df['close']
        print(f'-----加载 {symbol} 行情成功，共{len(df)}条数据 -----')
        return df

