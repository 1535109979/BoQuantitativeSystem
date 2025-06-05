import argparse

from BoQuantitativeSystem.engine import Engine


def main():
    parser = argparse.ArgumentParser(description='AutoBt - 自动化回测系统')
    parser.add_argument('--engine_mode', type=str, default='backtest',
                        help='系统模式 回测: backtest 实盘: trade')
    parser.add_argument('--source_type', type=str, default='CRYPTO',
                        help='选择市场 CRYPTO FUTURE STOCK')

    # 回测参数
    parser.add_argument('--start_time', type=str, default='2025-06-01 00:00:00',
                        help='回测开始时间')
    parser.add_argument('--settle_mode', type=str, default='trade_settle',
                        help='结算模式: trade_settle | daily_settle')


    args = parser.parse_args()

    Engine(args.engine_mode, args.source_type, args.settle_mode, args.start_time).start()


if __name__ == '__main__':
    main()