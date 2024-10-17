from common.remote import *
import traceback
import sys
from maintainer.app import AppStatistics, app_datas
from common.utils.log import logger
from common.utils import *
def load_app_infos():
    logger.info("update appInfos start...")
    try:
        apps = store_service_stub.getApps()
        for app_id in apps:
            if app_id not in app_datas:
                __add_new_app(app_id)

        logger.info("update appInfos end...")
    except Exception as err:
        logger.error('get apps meet error:'+ str(err))
        traceback.print_exception(*sys.exc_info())

def __add_new_app(app_id):
    logger.info("update appInfos create app_id = {} info".format(app_id))
    app_info = AppStatistics(
        app_id=app_id,
        index=flatl2_index())
    app_datas[app_id] = app_info