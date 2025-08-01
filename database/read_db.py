import sqlite3

import pandas as pd

from BoQuantitativeSystem.config.config import Configs

with sqlite3.connect(Configs.root_fp + 'database/' + 'bian_f_data.db') as conn:
    df = pd.read_sql('select * from account_value', conn)
    print(df)
    df = pd.read_sql('select * from trade_info', conn)
    sum_df = df.groupby('instrument')[['profit', 'commission']].sum().reset_index()
    count_df = df[df['offset'] == 'close'].groupby('instrument').size().reset_index(name='close_count')
    result = pd.merge(sum_df, count_df, on='instrument', how='left').fillna({'close_count': 0})
    print(df)
    print(result)
    # df = pd.read_sql('select * from order_info', conn)
    # print(df)



