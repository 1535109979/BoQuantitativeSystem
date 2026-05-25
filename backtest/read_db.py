import sqlite3
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class ReadDB:
    @classmethod
    def read_crypto(self, symbol, strat_time='2025-01-01 00:00:00'):
        print(f'-----开始加载 {symbol} 行情数据-----')
        db_fp = '/Users/edy/byt_pub/a_songbo/binance_client/backtest/binance_quote_data.db'
        table_name = f'future_{symbol.lower()}'
        with sqlite3.connect(db_fp) as conn:
            df = pd.read_sql(
                f'select * from {table_name} where start_time >= "{strat_time}" order by start_time DESC',
                conn)
            df = df.sort_values(by='start_time').reset_index(drop=True)
            df['symbol'] = symbol
            df['last_price'] = df['close']
        print(f'-----加载 {symbol} 行情成功，共{len(df)}条数据 -----')
        return df


def run_backtest():
    """回测：做多低beta / 做空高beta（每周轮动）"""
    db_fp = '/Users/edy/byt_pub/a_songbo/binance_client/backtest/binance_quote_data.db'
    symbols = ['btcusdt', 'dogeusdt', 'solusdt', 'bnbusdt', 'ethusdt', 'trxusdt', 'adausdt', 'xrpusdt']

    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d 00:00:00')

    # 1. 加载分钟数据，合成小时数据（最后一分钟的close为小时收盘价）
    print('=== 加载数据 ===')
    with sqlite3.connect(db_fp) as conn:
        hourly_close = {}
        for symbol in symbols:
            print(f'加载 {symbol}...')
            df = pd.read_sql(
                f'select start_time, close from future_{symbol} where start_time >= "{six_months_ago}" order by start_time',
                conn)
            if df.empty:
                print(f'  {symbol} 无数据')
                continue
            df['start_time'] = pd.to_datetime(df['start_time'])
            hourly = df.set_index('start_time')['close'].astype(float).resample('h').last().dropna()
            hourly_close[symbol] = hourly
            print(f'  {symbol}: {len(hourly)} 小时数据')

    close_df = pd.DataFrame(hourly_close)
    initial_cols = close_df.columns.tolist()
    print(f'\n合并后共 {len(close_df)} 小时数据 ({close_df.index[0]} ~ {close_df.index[-1]})')

    # 2. 计算小时收益率
    returns = close_df.pct_change().dropna()

    # 3. 每周轮动回测
    print('\n=== 运行回测 ===')

    # 按周一分组，取每组第一个小时为重平衡日
    rebalance_dates = [
        group.index[0]
        for _, group in returns.groupby(pd.Grouper(freq='W-MON'))
        if len(group) > 0
    ]

    # beta 计算最少需要 7 天数据
    min_lookback = 7 * 24

    portfolio_returns = []

    for i, rebal_date in enumerate(rebalance_dates):
        idx = returns.index.get_loc(rebal_date)
        if idx < min_lookback:
            continue

        # 用所有截至今日的历史数据计算 beta
        lookback = returns.iloc[:idx]

        # 等权指数收益率
        index_ret = lookback.mean(axis=1)

        # 计算每个币与指数的 beta
        betas = {}
        for sym in initial_cols:
            sym_ret = lookback[sym]
            cov = np.cov(sym_ret.values, index_ret.values)
            betas[sym] = cov[0, 1] / cov[1, 1]

        sorted_beta = sorted(betas.items(), key=lambda x: x[1])
        low_beta = [s[0] for s in sorted_beta[:4]]
        high_beta = [s[0] for s in sorted_beta[-4:]]

        if i % 10 == 0:
            beta_str = ', '.join(f'{s}={b:.3f}' for s, b in sorted_beta)
            print(f'  rebalance {rebal_date.date()}: {beta_str}')
            print(f'    long(低beta): {low_beta}, short(高beta): {high_beta}')

        # 计算下周的持仓收益
        if i < len(rebalance_dates) - 1:
            period_ret = returns.loc[rebal_date:rebalance_dates[i + 1]].iloc[:-1]
        else:
            period_ret = returns.loc[rebal_date:]

        if period_ret.empty:
            continue

        # 等权重：long = +1/4 each, short = -1/4 each
        long_ret = period_ret[low_beta].mean(axis=1)
        short_ret = period_ret[high_beta].mean(axis=1)
        portfolio_ret = long_ret - short_ret

        portfolio_returns.append(portfolio_ret)

    if not portfolio_returns:
        print('数据不足，无法运行回测')
        return

    portfolio_series = pd.concat(portfolio_returns).sort_index()
    cum_ret = (1 + portfolio_series).cumprod()

    # 4. 画图
    plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti SC', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    fig, axes = plt.subplots(2, 1, figsize=(16, 10))

    # 收益曲线
    axes[0].plot(cum_ret.index, cum_ret.values, linewidth=2, color='navy')
    axes[0].axhline(y=1, color='gray', linestyle='--', alpha=0.5)
    axes[0].set_title('低beta做多 / 高beta做空 每周轮动回测', fontsize=14)
    axes[0].set_ylabel('累计收益', fontsize=12)
    axes[0].grid(True, alpha=0.3)
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    # 回撤曲线
    rolling_max = cum_ret.expanding().max()
    drawdown = cum_ret / rolling_max - 1
    axes[1].fill_between(drawdown.index, 0, drawdown.values, color='red', alpha=0.3)
    axes[1].plot(drawdown.index, drawdown.values, color='red', linewidth=1)
    axes[1].set_ylabel('回撤', fontsize=12)
    axes[1].grid(True, alpha=0.3)
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()

    # 5. 统计指标
    total_cum = cum_ret.iloc[-1] - 1
    n_years = len(portfolio_series) / (365.25 * 24)
    ann_ret = (1 + total_cum) ** (1 / n_years) - 1
    ann_vol = portfolio_series.std() * np.sqrt(365.25 * 24)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
    max_dd = drawdown.min()
    calmar = ann_ret / abs(max_dd) if max_dd != 0 else 0
    win_rate = (portfolio_series > 0).sum() / len(portfolio_series)

    print(f'\n=== 回测统计 ===')
    print(f'回测期间: {portfolio_series.index[0]} ~ {portfolio_series.index[-1]}')
    print(f'总收益率: {total_cum:.2%}')
    print(f'年化收益率: {ann_ret:.2%}')
    print(f'年化波动率: {ann_vol:.2%}')
    print(f'夏普比率: {sharpe:.2f}')
    print(f'最大回撤: {max_dd:.2%}')
    print(f'卡玛比率: {calmar:.2f}')
    print(f'胜率(按小时): {win_rate:.2%}')


if __name__ == '__main__':
    run_backtest()
