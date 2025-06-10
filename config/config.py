import logging
import os
import platform

system = platform.system()


class Configs:
    engine_mode = 'trade'   #  backtest  trade
    account_type = 'CRYPTO'    #  CRYPTO  FUTURE


    position_multi_limit = 5
    dr = 0.002
    signal_reserve_time = 1200


    if system == 'Darwin':
        root_fp = '/Users/edy/byt_pub/BoQuantitativeSystem/'

    elif system == 'Linux':
        root_fp = '/a_songbo/BoQuantitativeSystem/'

    base_config = {
        'strategy_name': ['breakout', 'bid'], 'open_direction': 'LONG','open_volume': 30,
        'cover_count': 0, 'stop_profit_rate': 1.3, 'peak': 0, 'tough': 0,'cash': 30,
        'last_couer_price': 0,
        'cover_multi_list': [2, 4, 8, 16, 32, 64],
        'cover_decline_list': [5, 6, 7, 8, 9, 10], }

    instrument_configs = [
        {'instrument': 'LTCUSDT', 'windows': 550, 'roll_mean_period': 630, 'interval_period': 60, },
        # {'instrument': 'RLCUSDT', 'windows': 400, 'roll_mean_period': 120, 'interval_period': 860, },
        # {'instrument': 'ONDOUSDT', 'windows': 430, 'roll_mean_period': 200, 'interval_period': 710, },
        # {'instrument': 'AEVOUSDT', 'windows': 600, 'roll_mean_period': 350, 'interval_period': 320, },
        # {'instrument': 'BANDUSDT', 'windows': 730, 'roll_mean_period': 540, 'interval_period': 660, },
        # {'instrument': 'CELRUSDT', 'windows': 720, 'roll_mean_period': 610, 'interval_period': 400, },
        # {'instrument': 'MOVRUSDT', 'windows': 300, 'roll_mean_period': 300, 'interval_period': 900, },
        # {'instrument': 'NFPUSDT', 'windows': 390, 'roll_mean_period': 100, 'interval_period': 320, },
        # {'instrument': 'PORTALUSDT', 'windows': 600, 'roll_mean_period': 500, 'interval_period': 600, },
    ]

    ctp_setting = {
        "vn_config_home": os.path.join(os.path.expanduser('~'), ".vntrader"),
        'account_id': '210380', 'password': 'Songbo@1997', 'brokerid': '9999',
        'md_address': 'tcp://180.168.146.187:10212',
        'td_address': 'tcp://180.168.146.187:10202',
        # 'md_address': 'tcp://180.168.146.187:10131',
        # 'td_address': 'tcp://180.168.146.187:10130',
        'appid': 'simnow_client_test', 'auth_code': '0000000000000000'}

    crypto_setting = {
        'recvWindow': '5000',
        'stream_url': 'wss://fstream.binance.com',
        'base_url': 'https://fapi.binance.com',
        # 'api_key': '8kHJ8xMwb8wZkrTy17IVOym4CDo5qS6JFP8suvpsDaWCqjuBuIAn29HFYKuQM1bE',
        # 'secret_key': 'uUH1X2sz5jnMVhL44zxHiphnxhoQ5swPs62gFg4JFLCRayWwFr2MZJm9dJlaM2WK',
        'api_key': 'tw8xvSqYAXfqqTHWBKKuvETUcJ6w9BttMG6QIb7q7CceVrl74RdeChxeg05zfDg2',
        'secret_key': '81b9bXaVU7t0QhRQrFB5NfulRYYO7IFiR2D3rLOdrSlbGA2NYwxBvIy09JQPC1dL',
    }

