import fcntl

from common.config.config import config_info
import os
from common.utils.log import logger
from common import utils as ioutil
from matcher.app import AppState, app_states
# import matcher.matcher_manager as manager
import traceback
import sys
from common.utils.indexutil import flatl2_index,vecs_num, read_index

def check_and_load():
    try:
        logger.info("checker start")
        dir_path = config_info.app_dir
        ioutil.ensureFolder(dir_path)
        app_files = [os.path.join(dir_path, p) for p in sorted(os.listdir(dir_path))]
        # update info to cache
        for path in app_files:
            if path.endswith(".vec"):
                _process_vec_file(path)
            if path.endswith(".idx"):
                _process_idx_file(path)
        logger.info("checker end")
    except Exception as err:
        logger.error('check_and_load meet error:'+ str(err))
        traceback.print_exception(*sys.exc_info())
        pass

def _read_new_vectors_and_update_statistics(app_state, start_position):
    logger.info("read {} from {}".format(app_state.get_app_id(), start_position))
    vec_path = app_state.get_vec_file_path()
    with open(vec_path+".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        try:
            # 从上次读取位置开始更新辅助索引
            _, new_id_mapper = ioutil.get_vec_file_info(vec_path, start_position)
            app_state.get_id_mapper().update(new_id_mapper)
            # 更新统计信息
            app_state.set_vec_last_mtime(os.path.getmtime(vec_path))
            logger.info("{} file size is {}".format(vec_path, os.path.getsize(vec_path)))
            app_state.set_vec_file_length(os.path.getsize(vec_path))
            logger.info(
                "app_id:{}, vecs loaded from vec file:{}".format(app_state.get_app_id(),
                                                                 len(app_state.get_id_mapper())))
        except Exception as err:
            raise err # should not happened
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)



def _process_vec_file(path):
    app_id = ioutil.extract_appid(path)
    # 若未处理过此app，则全量读取vec文件，创建辅助索引
    if app_id not in app_states:
        logger.info("initialize {} from {}".format(app_id, path))
        app_states[app_id] = AppState(app_id=app_id, index=flatl2_index(), id_mapper={})
        _read_new_vectors_and_update_statistics(app_states[app_id], start_position=0)
        return

    # 若处理过，且vec存在更新，则从上次加载的位置开始，读取数据
    logger.info("load {} from {}".format(app_id, path))
    app_state:AppState = app_states[app_id]
    vec_path = app_state.get_vec_file_path()
    modify_time = os.path.getmtime(vec_path)
    if modify_time > app_state.get_vec_last_mtime():
        _read_new_vectors_and_update_statistics(app_state, start_position=app_state.get_vec_file_length())
    else:
        logger.info("No updated for {}".format(path))

def _process_idx_file(path):
    logger.info("try read {} ".format(path))
    app_id = ioutil.extract_appid(path)
    # 若未处理过此app，就加载
    if app_id not in app_states:
        logger.info("initialize {} from {}".format(app_id, path))
        app_states[app_id] = AppState(app_id=app_id, index=flatl2_index(), id_mapper={})
        load_index_and_update_statistics(app_states[app_id])
        return

    # 若处理过此app，且索引存在更新，则重新加载
    logger.info("load {} from {}".format(app_id, path))
    app_state:AppState = app_states[app_id]
    idx_path = app_state.get_index_file_path()
    modify_time = os.path.getmtime(idx_path)
    if modify_time > app_state.get_index_last_mtime():
        load_index_and_update_statistics(app_state)
    else:
        logger.info("No updated for {}".format(path))

# 获取app索引
def load_index_and_update_statistics(app_state:AppState):
    index_path = app_state.get_index_file_path()
    new_index = read_index(index_path)
    app_state.set_index(new_index)
    app_state.set_index_last_mtime(os.path.getmtime(index_path))
    logger.info(
            "app_id:{}, vecs in index file:{}".format(app_state.get_app_id(), vecs_num(app_state.get_index())))

