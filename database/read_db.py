import sqlite3
from datetime import datetime

import matplotlib.dates as mdates
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from BoQuantitativeSystem.config.config import Configs

with sqlite3.connect(Configs.root_fp + 'database/' + 'bian_f_data.db') as conn:
    df = pd.read_sql('select * from account_value', conn)
    df['posi'] = np.where(df['update_time'] < '2025-08-01 19:15:00', 50, 70)
    delta_bal = df['balance'].diff()
    df['cha'] = delta_bal / df['posi'].shift(1)
    df['cha'] = df['cha'].fillna(0)
    df['value'] = (df['cha'] * 100).cumsum()
    df['update_time'] = pd.to_datetime(df['update_time'])
    print(df)
    df_trade = pd.read_sql('select * from trade_info', conn)
    df_trade['update_time'] = pd.to_datetime(df_trade['update_time'])
    sum_df = df_trade.groupby('instrument')[['profit', 'commission']].sum().reset_index()
    count_df = df_trade[df_trade['offset'] == 'CLOSE'].groupby('instrument').size().reset_index(name='close_count')
    group_gain = pd.merge(sum_df, count_df, on='instrument', how='left').fillna({'close_count': 0})
    group_gain['profit'] = (group_gain['profit'] * 10).round(2).astype(str) + '%'
    group_gain['commission'] = (group_gain['commission'] * 10).round(2).astype(str) + '%'

    now = datetime.now()
    first_time = ( df_trade.groupby('instrument')['update_time'].min() )
    days_since_first = (now - first_time).dt.total_seconds() / (24 * 3600)
    days_df = (days_since_first.reset_index().rename(columns={'update_time': 'days_from_first'}).round(2))
    group_gain = pd.merge(group_gain, days_df, on='instrument', how='left')

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

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
        go.Scatter(x=df['update_time'], y=df['value'],
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



