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

    # stop_loss breakout bid
    strategy_list = [

        {'instrument': 'RLCUSDT', 'cash': 100,
         'windows': 400, 'roll_mean_period': 120, 'interval_period': 860,
         'strategy_name': ['stop_loss', 'breakout'], 'open_direction': 'LONG',
         'open_volume': 30, 'order_step_muti': 20, 'stop_loss_rate': 0,
         'cover_count': 1, 'last_couer_price': 2.3888,
         'cover_muti_list': [2, 4, 8, 16, 32, 64],
         'cover_decline_list': [5, 6, 7, 8, 9, 10],
         'peak': 2.1439, 'tough': 1.9825,
         'stop_profit_rate': 1.3,
         },

        {'instrument': 'ONDOUSDT', 'cash': 100,
         'windows': 430, 'roll_mean_period': 200, 'interval_period': 710,
         'strategy_name': ['stop_loss', 'breakout'], 'open_direction': 'LONG',
         'open_volume': 30, 'order_step_muti': 10, 'stop_loss_rate': 0,
         'cover_count': 1, 'last_couer_price': 1.1391,
         'cover_muti_list': [2, 4, 8, 16, 32, 64],
         'cover_decline_list': [7, 8, 9, 10, 11, 12],
         'peak': 0, 'tough': 0,
         'stop_profit_rate': 1.3,
         },
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
        'api_key': '8kHJ8xMwb8wZkrTy17IVOym4CDo5qS6JFP8suvpsDaWCqjuBuIAn29HFYKuQM1bE',       # bo
        'secret_key': 'uUH1X2sz5jnMVhL44zxHiphnxhoQ5swPs62gFg4JFLCRayWwFr2MZJm9dJlaM2WK',
        # 'api_key': 'tw8xvSqYAXfqqTHWBKKuvETUcJ6w9BttMG6QIb7q7CceVrl74RdeChxeg05zfDg2',     # hui
        # 'secret_key': '81b9bXaVU7t0QhRQrFB5NfulRYYO7IFiR2D3rLOdrSlbGA2NYwxBvIy09JQPC1dL',
    }

