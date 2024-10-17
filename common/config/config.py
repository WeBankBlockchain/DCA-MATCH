import os
from configparser import ConfigParser
import json

class GlobalConfig:
    def __init__(self, filename):
        cf = ConfigParser()
        cf.read(filename)
        self.app_dir = cf.get("app","appDir")

        self.port = cf.get("matcher", "port")
        self.tmp_dir = cf.get("matcher","tmpDir")
        self.index_load_interval_seconds = int(cf.get("matcher", "indexLoadIntervalSeconds"))
        self.scan_threshold = float(cf.get("matcher", "scanThreshold"))

        self.index_switch_threshold = int(cf.get("maintainer", "indexSwitchThreshold"))
        self.app_load_interval_seconds = int(cf.get('maintainer', "appLoadIntervalSeconds"))
        self.vectors_load_interval_seconds = int(cf.get('maintainer', "vectorsLoadIntervalSeconds"))
        self.remote_fetch_batch = int(cf.get('maintainer', "remoteFetchBatch"))
        self.ssd_reload_batch = int(cf.get('maintainer', "ssdReloadBatch"))
        self.retrain_threshold = json.loads(cf.get('maintainer', "retrainThreshold"))
        self.check_healthy_at=json.loads(cf.get('maintainer', "checkHealthyAt"))
        self.max_train_count=int(cf.get('maintainer', "maxTrainCount"))
        self.max_server_limit=int(cf.get('maintainer', "maxServerLimit"))

        self.store_url = cf.get("remote", "storeUrl")
        self.vc_url = cf.get("remote", "vcUrl")

        self.match_log_path = cf.get("log", "matchLogFile")
        self.wm_match_log_path = cf.get("log", "logFile")
        self.maintainer_log_path = cf.get("log", "maintainerLogFile")
        self.app_monitor_path = cf.get("log", "monitorFile")
        self.log_level = cf.get("log", "level")

# 配置实例
# os.chdir("..")
config_info = GlobalConfig('config.conf')


