from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UseInstrumentConfigBook:
    account_id: str
    instrument: str
    status: str
    cash: float
    windows: int
    roll_mean_period: int
    interval_period: int
    strategy_name: str
    open_direction: str
    stop_loss_rate: float
    stop_profit_rate: float
    open_rate: float
    win_stop_profit_rate: float
    loss_stop_profit_rate: float
    max_profit_rate: float
    order_price_delta: int
    order_price_type: str
    leverage: int
    param_json: str
    update_time: datetime
    daily_trade_flag: datetime

    @classmethod
    def create_by_row(cls, r):
        return UseInstrumentConfigBook(
            account_id=r.account_id,
            instrument=r.instrument,
            status=r.status,
            cash=r.cash,
            windows=r.windows,
            roll_mean_period=r.roll_mean_period,
            interval_period=r.interval_period,
            strategy_name=r.strategy_name,
            open_direction=r.open_direction,
            stop_loss_rate=r.stop_loss_rate,
            open_rate=r.open_rate,
            win_stop_profit_rate=r.win_stop_profit_rate,
            loss_stop_profit_rate=r.loss_stop_profit_rate,
            max_profit_rate=r.max_profit_rate,
            stop_profit_rate=r.stop_profit_rate,
            order_price_delta=r.order_price_delta,
            order_price_type=r.order_price_type,
            leverage=r.leverage,
            param_json=r.param_json,
            update_time=r.update_time,
            daily_trade_flag=r.daily_trade_flag,
        )

