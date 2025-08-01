import sqlite3

import pandas as pd

from BoQuantitativeSystem.config.config import Configs

with sqlite3.connect(Configs.root_fp + 'database/' + 'bian_f_data.db') as conn:
    df = pd.read_sql('select * from account_value', conn)
    print(df)
    df = pd.read_sql('select * from TradeInfo', conn)
    print(df)



