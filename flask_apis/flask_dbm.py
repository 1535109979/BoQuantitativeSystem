import requests
import json



class FlaskDBM:
    def __init__(self, url):
        self.url = url
        self.headers = {"Content-Type": "application/json"}

    def add_user_instrument_config(self, data):

        try:
            response = requests.post(self.url+'add_user_instrument_config', data=json.dumps(data), headers=self.headers)
            response.raise_for_status()  # 检查请求是否成功
            print("Response:", response.json())  # 打印响应内容
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)

    def update_user_instrument_config(self, data):
        try:
            response = requests.post(self.url+'update_user_instrument_config', data=json.dumps(data), headers=self.headers)
            response.raise_for_status()  # 检查请求是否成功
            print("Response:", response.json())  # 打印响应内容
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)

    def query_data(self, table_name):
        try:
            response = requests.get(self.url+ 'query_table_data', params={'table_name': table_name}, headers=self.headers)
            response.raise_for_status()  # 检查请求是否成功
            return response.json()
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)

    def query_all_user_instrument_config(self):
        try:
            response = requests.get(self.url+ 'query_user_instrument_config')
            response.raise_for_status()  # 检查请求是否成功
            print("Response:", response.json())  # 打印响应内容
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)

if __name__ == '__main__':

    url = 'http://127.0.0.1:5050/'
    # url = 'http://43.155.76.153:5050/'

    dbm = FlaskDBM(url)

    # dbm.query_all_user_instrument_config()

    data = dbm.query_data(table_name='table_updated_time')
    print(data)

    data = dbm.query_data(table_name='use_instrument_config')
    for row in data['data']:
        print(row)

    # data = {
    #     "account_id": "bo",
    #     "instrument": "1000whyusdt",
    #     "status": "ENABLE",
    #     "cash": 10,
    #     "windows": 200,
    #     "roll_mean_period": 500,
    #     "interval_period": 100,
    #     "strategy_name": ['stop_loss', 'breakout'],
    #     "open_direction": "long",
    #     "stop_loss_rate": 0.1,
    #     "stop_profit_rate": 1.3,
    #     "order_price_delta": 10,
    #     "order_price_type": "limit",
    #     "leverage": 2,
    #     "param_json": "{}"
    # }
    # dbm.add_user_instrument_config(data)



    # dbm.update_user_instrument_config(data)