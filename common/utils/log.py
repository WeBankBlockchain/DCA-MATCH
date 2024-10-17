import multiprocessing
import sys

from loguru import logger
from common.config.config import config_info

match_log = config_info.match_log_path
wm_match_log = config_info.wm_match_log_path
maintainer_log = config_info.maintainer_log_path
app_monitor_path = config_info.app_monitor_path
log_level = config_info.log_level

def app_monitor_filter(record):
    return "app" in record["extra"]

def match_log_filter(record):
    if  "app" not in record["extra"]:
        return multiprocessing.current_process().name.startswith('MatcherProcess')

def wm_match_log_filter(record):
    if  "app" not in record["extra"]:
        return multiprocessing.current_process().name.startswith('WaterMarkMatcherProcess')

def maintainer_log_filter(record):
    if  "app" not in record["extra"]:
        return multiprocessing.current_process().name.startswith('MaintainerProcess')


class Log:
    def __init__(self):
        self.logger = logger
        # 清空所有设置
        self.logger.remove()
        # 输出到文件的格式,注释下面的add',则关闭日志写入
        self.logger.add(match_log, level= log_level,
                        filter=match_log_filter,
                        format="[{level}]"
                               "[{time:YYYY-MM-DD HH:mm:ss.SSS}]"
                               "[{process.name}-{thread.name}] "  # 进程名
                               "{module}.{function}"  # 模块名.方法名
                               ":{line} | "  # 行号
                               "{message}",  # 日志内容
                        rotation="00:00",
                        retention="365 days",
                        compression = "gz",
                        enqueue = True)
        self.logger.add(wm_match_log, level= log_level,
                        filter=wm_match_log_filter,
                        format="[{level}]"
                               "[{time:YYYY-MM-DD HH:mm:ss.SSS}]"
                               "[{process.name}-{thread.name}] "  # 进程名
                               "{module}.{function}"  # 模块名.方法名
                               ":{line} | "  # 行号
                               "{message}",  # 日志内容
                        rotation="00:00",
                        retention="365 days",
                        compression = "gz",
                        enqueue = True)

        self.logger.add(maintainer_log, level= log_level,
                        filter=maintainer_log_filter,
                        format="[{level}]"
                               "[{time:YYYY-MM-DD HH:mm:ss.SSS}]"
                               "[{process.name}-{thread.name}] "  # 进程名
                               "{module}.{function}"  # 模块名.方法名
                               ":{line} | "  # 行号
                               "{message}",  # 日志内容
                        rotation="00:00",
                        retention="365 days",
                        compression = "gz",
                        enqueue = True)
        self.logger.add(app_monitor_path,
                        filter=app_monitor_filter,
                        level='INFO',
                        format="[{level}]"
                               "[{time:YYYY-MM-DD HH:mm:ss.SSS}]"
                               "[{process.name}-{thread.name}] "  # 进程名
                               "{message}",  # 日志内容
                        rotation="00:00",
                        retention="365 days",
                        compression = "gz",
                        enqueue = True)

        self.logger.add(sys.stdout, colorize=True,  format="[{level}]"
                               "[{time:YYYY-MM-DD HH:mm:ss.SSS}]"
                               "[{process.name}-{thread.name}] "  # 进程名
                               "{message}")
    def get_logger(self):
        return self.logger

logger = Log().get_logger()

