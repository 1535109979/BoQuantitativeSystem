import sqlite3
from datetime import datetime

import pandas
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from plotly.subplots import make_subplots

from BoQuantitativeSystem.flask_apis.flask_dbm import FlaskDBM

pandas.set_option("expand_frame_repr", False)
pandas.set_option("display.max_rows", 2000)
import pandas as pd

url = 'http://43.155.76.153:5050/'

dbm = FlaskDBM(url)
data = dbm.query_data(table_name='trade_info')
df_trade = pandas.DataFrame(data['data'])
df_trade['update_time'] = pd.to_datetime(df_trade['update_time'])
df_trade = df_trade[df_trade['update_time'] > '2025-08-21 13:15:00']

def process_symbol(df_symbol):
    symbol = df_symbol.iloc[0]['instrument']
    df_symbol = df_symbol.sort_values(by=['trade_time'])
    # print(df_symbol)
    df_close = df_symbol[df_symbol['offset'] == 'CLOSE'].reset_index(drop=True)
    df_close['sum_profit'] = df_close['profit'].cumsum()
    plt.plot(df_close['sum_profit'])
    plt.savefig(f'res/{symbol}.jpg')
    plt.clf()

df_trade.groupby('instrument').apply(process_symbol)
# quit()
sum_df = df_trade.groupby('instrument')[['profit', 'commission']].sum().reset_index()
count_df = df_trade[df_trade['offset'] == 'CLOSE'].groupby('instrument').size().reset_index(name='close_count')
group_gain = pd.merge(sum_df, count_df, on='instrument', how='left').fillna({'close_count': 0})
group_gain[['profit','commission']] = group_gain[['profit','commission']].round(8)
# print(group_gain)
data = dbm.query_data(table_name='account_value')
df_account = pandas.DataFrame(data['data'])
df_account['update_time'] = pd.to_datetime(df_account['update_time'])
df_account = df_account[df_account['update_time'] > '2025-08-21 13:15:00']
# print(df_account)


# 计算表格行高：每行 28 px + 表头 30 px
table_height = 30 + 28 * len(group_gain)

# 总图高 = 曲线高 + 间距 + 表格高
total_height = 350 + 80 + table_height

fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=False,
    vertical_spacing=0.15,  # 加大间距
    subplot_titles=['账户累计收益率曲线', '各标的收益率统计'],
    specs=[[{"type": "scatter"}],
           [{"type": "table"}]],
    row_heights=[350, table_height]  # 固定行高
)

# 曲线
fig.add_trace(
    go.Scatter(x=df_account['update_time'], y=df_account['balance'],
               mode='lines+markers', name='Value'),
    row=1, col=1
)
fig.update_xaxes(
    tickformat='%Y-%m-%d',  # 只保留日期
    dtick='D1',
    row=1, col=1
)
fig.update_yaxes(
    title_text='(%)',
    row=1, col=1
)
# 表格
fig.add_trace(
    go.Table(
        header=dict(values=list(group_gain.columns),
                    fill_color='paleturquoise', align='center'),
        cells=dict(values=[group_gain[c] for c in group_gain.columns],
                   fill_color='lavender', align='center')
    ),
    row=2, col=1
)

# 整体布局
fig.update_layout(
    height=total_height,
    margin=dict(l=40, r=40, t=60, b=40)
)

fig.show()



