import json
import logging
import multiprocessing
import os
import subprocess
import time
from datetime import datetime

import redis
from apscheduler.schedulers.blocking import BlockingScheduler
from peewee import fn

from BoQuantitativeSystem.config.config import Configs
from BoQuantitativeSystem.database.use_data import TableUpdatedTime, UseInstrumentConfig


class EngineSchedular:
    def __init__(self):
        self.table_update_time = {row.table_name: row.update_time for row in TableUpdatedTime.select()}
        self.create_logger()

        self.scheduler = BlockingScheduler()
        self.redis_pub_client = redis.Redis(**Configs.redis_setting)

    def start(self):
        self.scheduler.add_job(self.check_update_time, 'interval', seconds=5)

        self.check_update_time()
        self.scheduler.start()

    def check_update_time(self):
        if 'use_instrument_config' not in self.table_update_time.keys():
            max_time = (UseInstrumentConfig.select(fn.MAX(UseInstrumentConfig.update_time)).scalar())
            TableUpdatedTime(table_name='use_instrument_config', update_time=max_time).save()
            self.table_update_time['use_instrument_config'] = max_time
            self.logger.info(f'init save use_instrument_config {max_time}')
        else:
            table_time_data = TableUpdatedTime.get(TableUpdatedTime.table_name == 'use_instrument_config')
            self.logger.info(f'use_instrument_config max update_time:{table_time_data.update_time}')
            rows = (UseInstrumentConfig.select().where(UseInstrumentConfig.update_time > table_time_data.update_time))
            for row in rows:
                self.logger.info(f'updated rows:{row.__data__}')
                self.redis_pub_client.publish(row.account_id, json.dumps(row.__data__, default=str))
                self.logger.info(f'publish to {row.account_id} message={row.__data__}')
                table_time_data.update_time = datetime.now()
                table_time_data.save()

    def create_logger(self):
        self.logger = logging.getLogger('local_schedular')
        self.logger.setLevel(logging.DEBUG)
        log_fp = Configs.root_fp + 'logs/local_schedular.log'

        from logging.handlers import TimedRotatingFileHandler
        handler = TimedRotatingFileHandler(log_fp, when="midnight", interval=1, backupCount=7)
        handler.suffix = "%Y-%m-%d.log"  # 设置滚动后文件的后缀
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

if __name__ == '__main__':
    EngineSchedular().start()

