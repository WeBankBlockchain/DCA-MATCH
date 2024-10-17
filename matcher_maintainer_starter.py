#coding:UTF-8
from maintainer import start_loader
import schedule
from common.config.config import config_info
import threading
import time
from maintainer.task import *
import multiprocessing

process = multiprocessing.current_process()
# set the name
process.name = 'MaintainerProcess_'+str(process.pid)
def tasklist():
    #清空任务
    schedule.clear()
    #创建任务（它们都在同一个线程执行）
    schedule.every(config_info.app_load_interval_seconds).seconds.do(load_app_infos)
    schedule.every(config_info.vectors_load_interval_seconds).seconds.do(load_missing_vectors)
    for at in config_info.check_healthy_at:
        schedule.every().day.at(at).do(retrain_index_if_unhealthy)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def startTasks():
    thread = threading.Thread(target=tasklist)
    thread.start()
#

if __name__ == '__main__':
    start_loader.start()
    startTasks()