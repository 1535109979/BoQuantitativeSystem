import logging
import os
import platform

system = platform.system()


class Configs:
    engine_mode = 'trade'   #  backtest  trade
    account_type = 'CRYPTO'    #  CRYPTO  FUTURE


    position_multi_limit = 5
    dr = 0.002
    signal_wait_decline = False
    signal_reserve_time = 1200



    if system == 'Darwin':
        root_fp = '/Users/edy/a_songbo/'
        redis_setting = {
            "host": "127.0.0.1",
            "port": 6379,
            "password": "123456",
            "db": 1,
            "max_connections": 100
        }

    elif system == 'Linux':
        root_fp = '/a_songbo/'
        redis_setting = {
            "host": "10.5.0.5",
            "port": 6379,
            # "password": "123456",
            "db": 1,
            "max_connections": 100
        }

    for fp in [root_fp + 'database/', root_fp + 'logs/']:
        if not os.path.exists(fp):
            os.mkdir(fp)


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
        'stream_url': 'wss://fstream.binance.com/private',
        'base_url': 'https://fapi.binance.com',
    }

    @classmethod
    def get_setting(cls, account_id):
        # ip 43.155.76.153  203.175.14.43
        if account_id == 'bo':
            cls.crypto_setting.update({
                'api_key': '8kHJ8xMwb8wZkrTy17IVOym4CDo5qS6JFP8suvpsDaWCqjuBuIAn29HFYKuQM1bE',       # bo
                'secret_key': 'uUH1X2sz5jnMVhL44zxHiphnxhoQ5swPs62gFg4JFLCRayWwFr2MZJm9dJlaM2WK',
                'account_id': 'bo'
            })
        elif account_id == 'chao':
            cls.crypto_setting.update({
                'api_key':    'b9b98tFEOvo4hdRKkblM33l5hf8WAg99l4SS3aOGNsDKH8yOJ8cXu08JBIfE9BmJ',  # chao
                'secret_key': '1PYXKw57m7DtjFj4moeRtYlCSHwazR7NSyv75ysPeIxBcTfYcuFUdjc5f3B8Z8rR',
                'account_id': 'chao'
            })
        elif account_id == 'feng':
            cls.crypto_setting.update({
                'api_key':    'z8JT8HXJl7j2uqL7SRomhKuaYR7zA4PIH1gnPUBezUTvl47FRrkvLuTP9USEAYMH',  # chen
                'secret_key': 'lfyzvP3170nerHl3YhtqqkCilC7FhKNT3MOTvDh5NGx2hUCE2u4xCZXTfkjZM5br',
                'account_id': 'chen'
            })
        return cls.crypto_setting