from BoQuantitativeSystem.market.ms_gateway import MsGateway
from BoQuantitativeSystem.market.ms_grpc_server import MarkerGrpcServer


class MsEngine:
    def __init__(self):
        self.gateway = MsGateway()

    def start(self):
        try:
            self.gateway.loop.run_until_complete(MarkerGrpcServer(self.gateway).run())
        except Exception as e:
            pass

if __name__ == '__main__':
    MsEngine().start()
