import time

from maintainer.app import AppStatistics, app_datas
from maintainer.healthy_handler import *

def retrain_index_if_unhealthy():
    # 检查内存中记录的app数目，和索引数目，如果类型不一致或者数目不一致，或者跨过阈值，就重建

    for app_id in app_datas:
        try:
            logger.info("testing {}".format(app_id))
            curr_app: AppStatistics = app_datas[app_id]
            loaded_app = _refresh_from_disk(curr_app)
            # 检测是否存在vec文件被损坏
            if loaded_app.get_vec_count() != curr_app.get_vec_count() or loaded_app.get_last_vec_pos() != curr_app.get_last_vec_pos():
                logger.info("loaded data not match {}".format(app_id))
                _fix_unhealthy_app(curr_app, max_tries=5, interval=5)
                return
            # 检测
            healthy = is_app_healthy(curr_app)
            if not healthy:
                logger.info("app {} not healthy".format(app_id))
                _fix_unhealthy_app(curr_app, max_tries=5, interval=5)
            else:
                logger.info("app {} is healthy".format(app_id))
        except Exception as err:
            logger.error("Unexpected errors happens in for app {}. {}".format(app_id, str(err)))

    return

# 因为retrain是低频操作，尽量确保成功，不然下次就要很久了
def _fix_unhealthy_app(old_app:AppStatistics, max_tries=5, interval=5):
    tries = 0
    while tries < max_tries:
        try:
            logger.info("app {} is not healthy, rebuild".format(old_app.get_app_id()))
            rebuild_index(old_app)
            old_app.set_prev_vec_count(old_app.get_vec_count())
            logger.info("app {} rebuild complete".format(old_app.get_app_id()))
            return
        except Exception as err:
            tries += 1
            logger.error("err during fixing app {} with error:{} tries:{}".format(old_app.get_app_id(), str(err), tries))
            time.sleep(interval)

    logger.error("Fatal:app data {} fixed failed. check previous errors".format(old_app.get_app_id()))


def _refresh_from_disk(app: AppStatistics):
    newApp = AppStatistics(app.get_app_id(), app.get_index())

    last_vec_id, id_mapper = get_vec_file_info(app.get_vec_file_path())

    newApp.set_last_vec_pos(last_vec_id)
    newApp.set_vec_count(len(id_mapper))

    return newApp

