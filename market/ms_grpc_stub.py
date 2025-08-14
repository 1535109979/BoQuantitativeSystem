import time

import grpc

from BoQuantitativeSystem.grpc_files import ms_server_pb2_grpc, ms_server_pb2
from BoQuantitativeSystem.utils.thread import run_in_new_thread


class MarketStub:
    def __init__(self):
        channel = grpc.insecure_channel("0.0.0.0:6612")
        self.sub = ms_server_pb2_grpc.AsyncMarketServerStub(channel=channel)
        self.subscribed_instruments = set()

    def sub_account(self, account_type = 'CRYPTO'):
        self.sub.SubAccount(ms_server_pb2.AccountType(accounttype=account_type))

    @run_in_new_thread(thread_name="MS")
    def subscribe_stream_in_new_thread(self, on_quote, instruments=None):
        self.subscribe_stream(on_quote=on_quote, instruments=instruments)

    def subscribe_stream(self, on_quote, instruments=None):
        if instruments:
            self.subscribed_instruments.update(set(instruments))

        quote_reply_stream = self.sub.SubQuoteStream(ms_server_pb2.Symbols(symbols=instruments))

        for i in quote_reply_stream:
            on_quote(i.quote)

def on_quote(quote):
    print('get quote:', quote)

if __name__ == '__main__':
    MarketStub().subscribe_stream_in_new_thread(instruments=['ONDOUSDT'], on_quote=on_quote)
    # MarketStub().subscribe_stream_in_new_thread(instruments=['rb2509'], on_quote=on_quote)

    while 1:
        pass

