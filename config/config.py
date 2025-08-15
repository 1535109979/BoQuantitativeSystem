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
        root_fp = '/Users/edy/a_songbo/'

    elif system == 'Linux':
        root_fp = '/a_songbo/'

    for fp in [root_fp + 'database/', root_fp + 'logs/']:
        if not os.path.exists(fp):
            os.mkdir(fp)

    # stop_loss breakout bid
    strategy_list = [

        {'instrument': 'BOMEUSDT', 'cash': 10,
         'windows': 100, 'roll_mean_period': 800, 'interval_period': 100,
         'strategy_name': ['stop_loss', 'breakout'], 'open_direction': 'LONG',
         'open_volume': 30, 'order_step_muti': 10, 'stop_loss_rate': 0.1,
         'cover_count': 0, 'last_couer_price': 0,
         'peak': 0, 'tough': 0,
         'cover_muti_list': [2, 4, 8, 16, 32, 64],
         'cover_decline_list': [5, 6, 7, 8, 9, 10],
         'stop_profit_rate': 1.3,
         },

        {'instrument': '1000RATSUSDT', 'cash': 10,
         'windows': 500, 'roll_mean_period': 500, 'interval_period': 400,
         'strategy_name': ['stop_loss', 'breakout'], 'open_direction': 'LONG',
         'open_volume': 30, 'order_step_muti': 10, 'stop_loss_rate': 0.1,
         'cover_count': 0, 'last_couer_price': 0,
         'peak': 0, 'tough': 0,
         'cover_muti_list': [2, 4, 8, 16, 32, 64],
         'cover_decline_list': [7, 8, 9, 10, 11, 12],
         'stop_profit_rate': 1.3,
         },

        {'instrument': 'ALICEUSDT', 'cash': 10,
         'windows': 100, 'roll_mean_period': 200, 'interval_period': 400,
         'strategy_name': ['stop_loss', 'breakout'], 'open_direction': 'LONG',
         'open_volume': 30, 'order_step_muti': 10, 'stop_loss_rate': 0.1,
         'cover_count': 0, 'last_couer_price': 0,
         'peak': 0, 'tough': 0,
         'cover_muti_list': [2, 4, 8, 16, 32, 64],
         'cover_decline_list': [7, 8, 9, 10, 11, 12],
         'stop_profit_rate': 1.3,
         },

        {'instrument': '1000FLOKIUSDT', 'cash': 10,
         'windows': 100, 'roll_mean_period': 400, 'interval_period': 200,
         'strategy_name': ['stop_loss', 'breakout'], 'open_direction': 'LONG',
         'open_volume': 30, 'order_step_muti': 10, 'stop_loss_rate': 0.1,
         'cover_count': 0, 'last_couer_price': 0,
         'peak': 0, 'tough': 0,
         'cover_muti_list': [2, 4, 8, 16, 32, 64],
         'cover_decline_list': [7, 8, 9, 10, 11, 12],
         'stop_profit_rate': 1.3,
         },

        {'instrument': 'BAKEUSDT', 'cash': 10,
         'windows': 100, 'roll_mean_period': 200, 'interval_period': 200,
         'strategy_name': ['stop_loss', 'breakout'], 'open_direction': 'LONG',
         'open_volume': 30, 'order_step_muti': 10, 'stop_loss_rate': 0.1,
         'cover_count': 0, 'last_couer_price': 0,
         'peak': 0, 'tough': 0,
         'cover_muti_list': [2, 4, 8, 16, 32, 64],
         'cover_decline_list': [7, 8, 9, 10, 11, 12],
         'stop_profit_rate': 1.3,
         },

        {'instrument': 'GTCUSDT', 'cash': 10,
         'windows': 100, 'interval_period': 700, 'roll_mean_period': 200,
         'strategy_name': ['stop_loss', 'breakout'], 'open_direction': 'LONG',
         'open_volume': 30, 'order_step_muti': 10, 'stop_loss_rate': 0.1,
         'cover_count': 0, 'last_couer_price': 0,
         'peak': 0, 'tough': 0,
         'cover_muti_list': [2, 4, 8, 16, 32, 64],
         'cover_decline_list': [7, 8, 9, 10, 11, 12],
         'stop_profit_rate': 1.3,
         },

        {'instrument': 'MYROUSDT', 'cash': 10,
         'windows': 200, 'interval_period': 100, 'roll_mean_period': 300,
         'strategy_name': ['stop_loss', 'breakout'], 'open_direction': 'LONG',
         'open_volume': 30, 'order_step_muti': 10, 'stop_loss_rate': 0.1,
         'cover_count': 0, 'last_couer_price': 0,
         'peak': 0, 'tough': 0,
         'cover_muti_list': [2, 4, 8, 16, 32, 64],
         'cover_decline_list': [7, 8, 9, 10, 11, 12],
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
        # 'api_key': 'R8cR2rb6822fDtpdL7nFX9fNsoC8WdaNfK4K38C8vQrbsHuuE8WmSne0t29gRsN8',     # chao
        # 'secret_key': 'eHTwScKu61eYJSwzEe6tHcyavKOfROino1jncIuQnE8beMh4ljRXcXJD0Uzuadcj',
    }

    redis_setting = {
        "host": "43.155.76.153",
        "port": 6379,
        "password": "123456",
        "db": 1,
        "max_connections": 100
    }

