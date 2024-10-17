

from functools import wraps
import time
from common.utils.log import logger


def timeConsumer(type):
    def consuming(func):
        @wraps(func)
        def count(*args, **kwargs):
            start = time.time_ns() 
            result = func(*args, **kwargs)
            end = time.time_ns()
            logger.info("type {} use time = {}".format(type, str(end-start)))
            return result
        return count
    return consuming
