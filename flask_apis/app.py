from flask import Flask, render_template, request, redirect, url_for, jsonify

from BoQuantitativeSystem.database.use_data import UseInstrumentConfig

app = Flask(__name__)

@app.route('/')
def index():
    return 'hello'

@app.route('/update_config', methods=['POST'])
def update_config():
    data = request.get_json(force=True)
    print(data)

    return jsonify({'errcode': 0, 'errmsg': 'ok'})

@app.route('/query_all_user_instrument_config', methods=['GET'])
def query_all():
    instrument = request.args.get('instrument')
    rows = UseInstrumentConfig.select()
    if instrument:
        rows = rows.where(UseInstrumentConfig.instrument == instrument)
    data = [
        {
            **row.__data__,  # 所有字段
            'update_time': row.update_time.isoformat()
        }
        for row in rows
    ]
    return jsonify({'errcode': 0, 'data': data})

@app.route('/update_user_instrument_config', methods=['POST'])
def update_user_instrument_config():
    try:
        payload = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify({"errcode": 400, "errmsg": "JSON 解析失败"}), 400
    print(payload)
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
    row.save()

    return jsonify({"errcode": 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)