import logging
import platform

system = platform.system()


class Configs:
    account_type = 'CRYPTO'
    position_multi_limit = 5
    dr = 0.002
    signal_reserve_time = 1200

    db_fp = '/Users/edy/byt_pub/a_songbo/binance_client/backtest/binance_quote_data.db'

    if system == 'Darwin':
        root_fp = '/Users/edy/byt_pub/BoQuantitativeSystem/'

    elif system == 'Linux':
        root_fp = '/a_songbo/'

    base_config = {
        'strategy_name': ['breakout', 'bid'], 'open_direction': 'LONG','open_volume': 30,
        'cover_count': 0, 'stop_profit_rate': 1.3, 'peak': 0, 'tough': 0,'cash': 30,
        'last_couer_price': 0,
        'cover_multi_list': [2, 4, 8, 16, 32, 64],
        'cover_decline_list': [5, 6, 7, 8, 9, 10], }

    instrument_configs = [
        {'instrument': 'ltcusdt', 'windows': 550, 'roll_mean_period': 630, 'interval_period': 60, },
        # {'instrument': 'rlcusdt', 'windows': 400, 'roll_mean_period': 120, 'interval_period': 860, },
        # {'instrument': 'ondousdt', 'windows': 430, 'roll_mean_period': 200, 'interval_period': 710, },
        # {'instrument': 'aevousdt', 'windows': 600, 'roll_mean_period': 350, 'interval_period': 320, },
        # {'instrument': 'bandusdt', 'windows': 730, 'roll_mean_period': 540, 'interval_period': 660, },
        # {'instrument': 'celrusdt', 'windows': 720, 'roll_mean_period': 610, 'interval_period': 400, },
        # {'instrument': 'movrusdt', 'windows': 300, 'roll_mean_period': 300, 'interval_period': 900, },
        # {'instrument': 'nfpusdt', 'windows': 390, 'roll_mean_period': 100, 'interval_period': 320, },
        # {'instrument': 'portalusdt', 'windows': 600, 'roll_mean_period': 500, 'interval_period': 600, },
    ]




