import asyncio

import grpc

from BoQuantitativeSystem.grpc_files import ms_server_pb2_grpc, ms_server_pb2


class MarkerGrpcServer(ms_server_pb2_grpc.AsyncMarketServerServicer):
    def __init__(self, gateway):
        self.gateway = gateway
        self.server = None

    async def SubAccount(self, request, context):
        peer = context.peer()
        self.gateway.logger.info(f'服务器接收到{peer}的数据,{request.accounttype}')
        self.gateway.sub_account(request.accounttype)

        return ms_server_pb2.FlagReply(flag=True)

    async def SubQuoteStream(self, request, context):
        peer = context.peer()
        self.gateway.logger.info(f'服务器接收到{peer}的数据,{request.symbols}')

        quote_writer = self.gateway.get_or_create_subscriber(peer, context)

        symbols = set(request.symbols)

        need_sub = symbols.difference(quote_writer.subscribe_symbol)
        if need_sub:
            self.gateway.add_subscribe(need_sub=list(need_sub), quote_writer=quote_writer)

        while not context.done():
            await asyncio.sleep(600)

    async def run(self):
        self.server = grpc.aio.server()
        self.server.add_insecure_port("0.0.0.0:6612")
        ms_server_pb2_grpc.add_AsyncMarketServerServicer_to_server(self, self.server)
        await self.server.start()
        await self.server.wait_for_termination()


