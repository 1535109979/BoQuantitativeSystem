import logging
import platform

system = platform.system()


class Configs:
    dr = 0.002
    signal_reserve_time = 1200

    if system == 'Darwin':
        root_fp = '/Users/edy/byt_pub/'

    elif system == 'Linux':
        root_fp = '/a_songbo/'






