from datetime import datetime

from peewee import *

from BoQuantitativeSystem.database.dbm import *


class UseInstrumentConfig(Model):
    id = AutoField(primary_key=True)
    account_id = CharField()
    instrument = CharField()
    status = CharField()
    cash = FloatField()
    windows = IntegerField()
    roll_mean_period = IntegerField()
    interval_period = IntegerField()
    strategy_name = CharField()
    open_direction = CharField()
    stop_loss_rate = FloatField()
    stop_profit_rate = FloatField()
    open_rate = FloatField()
    win_stop_profit_rate = FloatField()
    loss_stop_profit_rate = FloatField()
    max_profit_rate = FloatField()
    order_price_delta = IntegerField()
    order_price_type = CharField()
    leverage = IntegerField()
    param_json = CharField()
    daily_trade_flag = DateTimeField()

    update_time = DateTimeField()

    class Meta:
        database = SqliteDatabaseManage().get_connect()
        table_name = 'use_instrument_config'

class TableUpdatedTime(Model):
    id = AutoField(primary_key=True)
    table_name= CharField()
    update_time = DateTimeField()

    class Meta:
        database = SqliteDatabaseManage().get_connect()
        table_name = 'table_updated_time'


def initialize_database():
    db = SqliteDatabaseManage().get_connect()
    tables = [TradeInfo, OrderInfo, AccountValue, Subtest, UseInstrumentConfig, TableUpdatedTime]
    db.create_tables(tables, safe=True)

# 当模块被导入时自动执行
initialize_database()


if __name__ == '__main__':
    # UseInstrumentConfig.create_table()
    # TableUpdatedTime.create_table()


    # use_instrument_configs = UseInstrumentConfig.select()
    # for use_instrument_config in use_instrument_configs:
    #     print(use_instrument_config.__data__)

    # update_date = UseInstrumentConfig.get(UseInstrumentConfig.instrument=='BNBUSDT_XRPUSDT')
    # update_date.update_time = datetime.now()
    # update_date.status = 'UNABLE'
    # update_date.save()


    save_data = UseInstrumentConfig(
        account_id='chao',
        instrument='BNBUSDT_ADAUSDT',
        open_rate=1,
        win_stop_profit_rate=4,
        loss_stop_profit_rate=3,
        daily_trade_flag=0,
        max_profit_rate=0,
        param_json={},
        status='ENABLE',
        cash=200,
        windows=100,
        roll_mean_period=400,
        interval_period=200,
        strategy_name=['rate_diff'],
        open_direction='LONG',
        stop_loss_rate=10,
        stop_profit_rate=1.3,
        order_price_delta=10,
        order_price_type='LIMIT',
        leverage=1,
        update_time=datetime.now(),
    )
    save_data.save()


