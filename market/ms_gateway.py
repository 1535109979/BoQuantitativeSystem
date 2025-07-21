import logging
import threading
import time
from asyncio import events
import traceback
import asyncio

from BoQuantitativeSystem.config.config import Configs
from BoQuantitativeSystem.grpc_files import ms_server_pb2
from BoQuantitativeSystem.market.bian_future_api.bian_future_md import BiFutureMdApi
from BoQuantitativeSystem.market.quote_writer import QuoteWriter
from BoQuantitativeSystem.utils.dingding import Dingding
from BoQuantitativeSystem.utils.sys_exception import common_exception


class MsGateway(object):
    def __init__(self):
        self.loop = events.new_event_loop()
        self.logger = None
        self.client = None

        self.sub_instruments = set()
        self.quote_subscriber = dict()

        self.create_logger()

        self.sub_account(Configs.account_type)

    def sub_account(self, account_type):
        self.logger.info(f'sub_account: {account_type}')
        if account_type == 'CRYPTO':
            self.client = BiFutureMdApi(self)
            self.client.connect()
            # Dingding.send_msg('币安行情服务启动成功')
        if account_type == 'FUTURE':
            from BoQuantitativeSystem.market.ctp_vn_api.vn_md_api import VnMdApi
            self.client = VnMdApi(self)


    def get_api_configs(self):
        if Configs.account_type == 'CRYPTO':
            return {'stream_url': 'wss://fstream.binance.com'}

        elif Configs.account_type == 'FUTURE':
            return Configs.ctp_setting

    def add_subscribe(self, need_sub, quote_writer: QuoteWriter):
        if not self.client:
            self.logger.info('not client')
            Dingding.send_msg('not client')
            return
        self.client.subscribe(need_sub)

        for symbol in need_sub:
            self.sub_instruments.update([symbol])
            if symbol not in quote_writer.subscribe_symbol:
                quote_writer.add_symbol([symbol])

    @common_exception(log_flag=True)
    def on_quote(self, quote):
        quote = {k: str(v) for k, v in quote.items() if v is not None}
        quote['ms_gateway_timestamp'] = str(time.time())
        if self.quote_subscriber:
            for p, q in self.quote_subscriber.items():
                if quote['symbol'] in q.subscribe_symbol:
                    self.send_quote(q, quote)
        self.logger.info(f'{quote["symbol"]} ms_gateway_timestamp:{quote["ms_gateway_timestamp"]}')

    def send_quote(self, q, quote):
        try:
            future = asyncio.run_coroutine_threadsafe(q.writer.write(self.create_grpc_reply(quote=quote)), self.loop)
            future.result()
        except:
            traceback.print_exc()

    def create_grpc_reply(self, quote):
        return ms_server_pb2.Quote(quote=quote)

    def add_subscriber(self, peer, context):
        quote_writer = QuoteWriter(context)
        self.quote_subscriber[peer] = quote_writer
        return quote_writer

    def get_or_create_subscriber(self,peer,context):
        quote_writer = self.quote_subscriber.get(peer)
        if not quote_writer:
            quote_writer = self.add_subscriber(peer,context)
        return quote_writer

    def cancel_subscriber(self, peer):
        self.quote_subscriber.pop(peer)

    def on_error(self, msg):
        self.logger.error(msg)
        Dingding.send_msg(msg)

    def on_front_disconnected(self, msg):
        self.logger.error(msg)
        Dingding.send_msg(msg)

    def create_logger(self):
        self.logger = logging.getLogger('bi_future_ms')
        self.logger.setLevel(logging.DEBUG)
        log_fp = Configs.root_fp + 'logs/bi_future_ms.log'

        from logging.handlers import TimedRotatingFileHandler
        handler = TimedRotatingFileHandler(log_fp, when="midnight", interval=1, backupCount=7)
        handler.suffix = "%Y-%m-%d.log"  # 设置滚动后文件的后缀
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def on_login_success(self):
        # Dingding.send_msg('ctp行情服务启动成功')
        pass
