from dataclasses import dataclass, field
from typing import Dict

from BoQuantitativeSystem.trade.do.instrument_book import InstrumentBook
from BoQuantitativeSystem.trade.do.position import InstrumentPositionBook, InstrumentPosition
from BoQuantitativeSystem.trade.do.rtn_trade import RtnTrade
from BoQuantitativeSystem.utils import type_util
from BoQuantitativeSystem.utils.exchange_enum import Direction, OffsetFlag


@dataclass
class AccountBook:
    """ 账户信息 """
    avail: float = 0
    balance: float = 0
    position_multi: float = 0
    position_sum_cost: float = 0

    base_instrument: str = field(default="USDT")
    data: dict = field(default_factory=dict)

    # 持仓数据字典 { vt_symbol : InstrumentPositionBook }
    position_books: Dict[str, InstrumentPositionBook] = field(default_factory=dict)

    # 合约属性字典 { vt_symbol: InstrumentBook }
    instrument_books: Dict[str, InstrumentBook] = field(default_factory=dict)

    def update_data(self, data):
        self.avail = type_util.get_precision_number(
            number=data.get("availableBalance"), precision=8, default=0)
        self.balance = type_util.get_precision_number(
            number=data.get("marginBalance"), precision=8, default=0)
        self.cal_position_multi()

    def create_instrument_book(self, vt_symbol: str):
        return InstrumentBook(vt_symbol=vt_symbol)

    def get_instrument_book(self, vt_symbol: str) -> InstrumentBook:
        """ 获取合约属性 """
        instrument_book: InstrumentBook = self.instrument_books.get(vt_symbol)
        if not instrument_book:
            instrument_book = self.create_instrument_book(vt_symbol)
            self.instrument_books.setdefault(vt_symbol, instrument_book)
        return instrument_book

    def get_instrument_position_book(self, vt_symbol: str) -> InstrumentPositionBook:
        """ 获取合约持仓信息 """
        position_book: InstrumentPositionBook = self.position_books.get(vt_symbol)
        if not position_book:
            position_book = InstrumentPositionBook(vt_symbol)
            self.position_books.setdefault(vt_symbol, position_book)
        return position_book

    def get_instrument_position(self, vt_symbol: str, direction: Direction) -> InstrumentPosition:
        """ 获取合约指定多空方向的持仓数量 """
        return self.get_instrument_position_book(vt_symbol).get_by_direction(direction)

    def update_by_trade_rtn(self, rtn: RtnTrade) -> InstrumentPosition:
        """ 根据成交回报信息更新账户和持仓信息 """
        position: InstrumentPosition = self.get_instrument_position(
            f"{rtn.instrument}.{rtn.exchange_type}", direction=rtn.direction)
        position.update_by_trade_rtn(rtn)

        # 更新账户可用资金
        if OffsetFlag.is_open_by_name(offset_flag=rtn.offset_flag, direction=rtn.direction):
            self.avail -= rtn.margin
        else:
            self.avail += rtn.margin

        self.cal_position_multi()
        return position

    def cal_position_multi(self):
        self.position_sum_cost = 0
        for k, pb in self.position_books.items():
            print(pb.long_position)
            print(pb.short_position)
            if pb.long_position.cost_amount:
                self.position_sum_cost += pb.long_position.cost_amount
            if pb.short_position.cost_amount:
                self.position_sum_cost += pb.short_position.cost_amount

        if self.balance and self.position_sum_cost:
            self.position_multi = round(self.position_sum_cost / self.balance, 2)

