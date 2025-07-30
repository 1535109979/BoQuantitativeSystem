import sqlite3

import pandas as pd




with sqlite3.connect('bian_f_data.db') as conn:
    df = pd.read_sql('select * from account_value', conn)
    print(df)



