from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, jsonify

from BoQuantitativeSystem.database.dbm import AccountValue, TradeInfo
from BoQuantitativeSystem.database.use_data import UseInstrumentConfig, TableUpdatedTime

app = Flask(__name__)

@app.route('/')
def index():
    return 'hello'

@app.route('/query_last_account_value', methods=['POST'])
def query_last_account_value():
    data = request.json

    latest = AccountValue.select().where(AccountValue.account_id == data['account_id']).order_by(
        AccountValue.update_time.desc()).first()
    if latest is None:
        jsonify({'errcode': 1, 'errmsg': '没有数据'}), 400
    else:
        return jsonify({'errcode': 0, 'errmsg': '查询成功', 'data': {
        'id': latest.id,
        'account_id': latest.account_id,
        'balance': latest.balance,
        'bnb': latest.bnb,
        'position_multi': latest.position_multi,
    }})

@app.route('/query_table_data', methods=['GET'])
def query_table_data():
    table_name_map = {
        'use_instrument_config': UseInstrumentConfig,
        'account_value': AccountValue,
        'trade_info': TradeInfo,
        'table_updated_time': TableUpdatedTime,
        }

    table_name = request.args.get('table_name')
    if table_name_map.get(table_name):
        rows = table_name_map.get(table_name).select()

        data = [
            {
                **row.__data__,  # 所有字段
                'update_time': row.update_time
            }
            for row in rows
        ]
        return jsonify({'errcode': 0, 'data': data})
    else:
        return jsonify({'errcode': 1, 'errmsg': '没有这个表'}), 400

@app.route('/query_user_instrument_config', methods=['GET'])
def query_user_instrument_config():
    instrument = request.args.get('instrument')
    rows = UseInstrumentConfig.select()
    if instrument:
        rows = rows.where(UseInstrumentConfig.instrument == instrument)
    data = [
        {
            **row.__data__,  # 所有字段
            'update_time': row.update_time
        }
        for row in rows
    ]
    return jsonify({'errcode': 0, 'data': data})

@app.route('/add_user_instrument_config', methods=['POST'])
def add_user_instrument_config():
    # 获取请求中的 JSON 数据
    data = request.json

    # 检查必要的字段是否存在
    required_fields = [
        'account_id', 'instrument', 'status', 'cash', 'windows', 'roll_mean_period',
        'interval_period', 'strategy_name', 'open_direction', 'stop_loss_rate',
        'stop_profit_rate', 'order_price_delta', 'order_price_type', 'leverage',
        'param_json'
    ]
    if not all(field in data for field in required_fields):
        return jsonify({'errcode': 1, 'errmsg': '缺少必要的字段'}), 400

    # 提取字段值
    account_id = data['account_id']
    instrument = data['instrument']
    status = data['status']
    cash = data['cash']
    windows = data['windows']
    roll_mean_period = data['roll_mean_period']
    interval_period = data['interval_period']
    strategy_name = data['strategy_name']
    open_direction = data['open_direction']
    stop_loss_rate = data['stop_loss_rate']
    stop_profit_rate = data['stop_profit_rate']
    order_price_delta = data['order_price_delta']
    order_price_type = data['order_price_type']
    leverage = data['leverage']
    param_json = data['param_json']

    # 可选字段：update_time，默认为当前时间
    update_time = data.get('update_time', datetime.now())

    try:
        new_config = UseInstrumentConfig.create(
            account_id=account_id,
            instrument=instrument,
            status=status,
            cash=cash,
            windows=windows,
            roll_mean_period=roll_mean_period,
            interval_period=interval_period,
            strategy_name=strategy_name,
            open_direction=open_direction,
            stop_loss_rate=stop_loss_rate,
            stop_profit_rate=stop_profit_rate,
            order_price_delta=order_price_delta,
            order_price_type=order_price_type,
            leverage=leverage,
            param_json=param_json,
            update_time=update_time
        )
        return jsonify({'errcode': 0, 'errmsg': '添加成功', 'data': {
            'id': new_config.id,
            'account_id': new_config.account_id,
            'instrument': new_config.instrument,
            'status': new_config.status,
            'cash': new_config.cash,
            'windows': new_config.windows,
            'roll_mean_period': new_config.roll_mean_period,
            'interval_period': new_config.interval_period,
            'strategy_name': new_config.strategy_name,
            'open_direction': new_config.open_direction,
            'stop_loss_rate': new_config.stop_loss_rate,
            'stop_profit_rate': new_config.stop_profit_rate,
            'order_price_delta': new_config.order_price_delta,
            'order_price_type': new_config.order_price_type,
            'leverage': new_config.leverage,
            'param_json': new_config.param_json,
            'update_time': new_config.update_time.isoformat()
        }})
    except Exception as e:
        return jsonify({'errcode': 1, 'errmsg': str(e)}), 500

@app.route('/update_user_instrument_config', methods=['POST'])
def update_user_instrument_config():
    try:
        payload = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify({"errcode": 400, "errmsg": "JSON 解析失败"}), 400

    account_id = payload.pop("account_id", None)
    instrument = payload.pop("instrument", None)
    if not account_id or not instrument:
        return jsonify({"errcode": 400, "errmsg": "缺少 account_id 或 instrument"}), 400

    row = (UseInstrumentConfig.select()
           .where((UseInstrumentConfig.account_id == account_id) &
                  (UseInstrumentConfig.instrument == instrument))
           .first())
    if not row:
        return jsonify({"errcode": 404, "errmsg": "记录不存在"}), 404

    for key, value in payload.items():
        if hasattr(row, key):
            setattr(row, key, value)
    row.update_time = datetime.now()
    row.save()

    return jsonify({"errcode": 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)