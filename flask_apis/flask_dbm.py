import requests
import json



class FlaskDBM:
    def __init__(self):
        self.url = 'http://43.155.76.153:5050/'
        self.headers = {"Content-Type": "application/json"}

    def add_user_instrument_config(self):
        data = {
            "account_id": "12345",
            "instrument": "example_instrument",
            "status": "active",
            "cash": 10000.0,
            "windows": 10,
            "roll_mean_period": 5,
            "interval_period": 3,
            "strategy_name": "example_strategy",
            "open_direction": "long",
            "stop_loss_rate": 0.05,
            "stop_profit_rate": 0.1,
            "order_price_delta": 10,
            "order_price_type": "limit",
            "leverage": 2,
            "param_json": "{}"
        }
        try:
            response = requests.post(self.url+'add_user_instrument_config', data=json.dumps(data), headers=self.headers)
            response.raise_for_status()  # 检查请求是否成功
            print("Response:", response.json())  # 打印响应内容
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)

    def query_data(self, table_name):
        try:
            response = requests.get(self.url+ 'query_table_data', params={'table_name': table_name}, headers=self.headers)
            response.raise_for_status()  # 检查请求是否成功
            print("Response:", response.json())  # 打印响应内容
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)

    def query_all_user_instrument_config(self):
        try:
            response = requests.get(self.url+ 'query_all_user_instrument_config')
            response.raise_for_status()  # 检查请求是否成功
            print("Response:", response.json())  # 打印响应内容
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)

if __name__ == '__main__':
    dbm = FlaskDBM()

    dbm.query_all_user_instrument_config()