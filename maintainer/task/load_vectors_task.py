import maintainer.app
from common import remote
import sys
import traceback

from maintainer.healthy_handler import *
from maintainer.app import app_datas, AppStatistics

def load_missing_vectors():
    try:
        logger.info("update index start...")
        for key in maintainer.app.app_datas:
            app_data:AppStatistics = maintainer.app.app_datas[key]
            logger.info('[Before update] app {appid}, app vectors:{appVecCount}, '
                        'last pos:{lastPos}, index type:{indexType}, total:{total}',
                        appid=app_data.get_app_id(),
                        appVecCount=app_data.get_vec_count(),
                        lastPos=app_data.get_last_vec_pos(),
                        indexType=idx_type(app_data.get_index()),
                        total = vecs_num(app_data.get_index()))

            # 获取store向量
            allVectors = _all_vectors_count()
            batch = min(config_info.remote_fetch_batch, config_info.max_server_limit - allVectors)
            logger.info("current sever has {} vectors, server limit {} .app id {} will fetch {} ".format(allVectors, config_info.max_server_limit, app_data.get_app_id(), batch))
            vectors = remote.store_service_stub.getVectors(
                app_id=app_data.get_app_id(),
                last_id=app_data.get_last_vec_pos(),
                batch=batch)

            if len(vectors) == 0:
                continue
            logger.info("{cnt} loaded for app {appId}", cnt=len(vectors), appId=app_data.get_app_id())

            # 更新索引
            _update_app_index(app_data, vectors)

            logger.info('[After update] app {app}, app vectors:{appVecCount}, '
                        'last pos:{lastPos}, index type:{indexType}, total:{total}',
                        app=app_data.get_app_id(),
                        appVecCount=app_data.get_vec_count(),
                        lastPos=app_data.get_last_vec_pos(),
                        indexType=idx_type(app_data.get_index()),
                        total = vecs_num(app_data.get_index()))

        logger.info("update index end")
    except Exception as err:
        logger.error('load vectors meet error:' + str(err))
        traceback.print_exception(*sys.exc_info())


def _update_app_index(app_data: AppStatistics, vectors):
    # 写入向量文件
    _write_vec(app_data, vectors, app_data.get_vec_file_path())
    # 更新内存中的索引(不做训练)
    _update_index(app_data, vectors)
    # 更新内存统计信息
    cur_cnt = app_data.get_vec_count()
    new_cnt = cur_cnt + len(vectors)
    app_data.set_vec_count(new_cnt)
    app_data.set_last_vec_pos(vectors[len(vectors) - 1]['pkId'])
    # 如果数目达到升级条件，就升级
    if not type_match(app_data):
        logger.info("app {} should be rebuilt because it reaches upgrade condition".format(app_data.get_app_id()))
        rebuild_index(app_data)
    # 索引写入磁盘
    write_index(app_data.get_index(), app_data.get_index_file_path())


def _update_index(app, vectors):
    ids = numpy.array([v['pkId'] for v in vectors]).astype('int64')
    vecs = numpy.array([v['feature'] for v in vectors]).astype('float32')

    index = app.get_index()
    index.add_with_ids(vecs, ids)
    logger.info("add vectors to {toType}. app_id:{appId}",  toType=idx_type(index), appId=app.get_app_id())

def _write_vec(app_info, vectors, vec_file_path):

    if app_info.get_vec_count() != 0 and not os.path.exists(vec_file_path):
        logger.error("on _write_vec {}: file lost".format(app_info.get_app_id()))
        app_info.reset()
        raise FileNotFoundError('File lost for '+app_info.get_app_id())
        return
    # a保证追加，b保证binary
    with open(vec_file_path + ".lock", 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            with open(vec_file_path, 'ab') as f:

                for item in vectors:
                    pk_id = item['pkId']
                    file_id = item['fileId']
                    vector = item['feature']
                    vector = numpy.array(vector).astype('float32')
                    pickle.dump(pk_id, f)
                    pickle.dump(file_id, f)
                    pickle.dump(vector, f)
                logger.info("appId = {app_id} _write_vec finish", app_id=app_info.get_app_id())
        except Exception as err:
            logger.error("Error happened on _write_vec {}: {}".format(app_info.get_app_id(), str(err)))
            app_info.reset()
            raise err
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)




def _all_vectors_count():
    ret = 0
    for key in app_datas:
        app_data:AppStatistics = app_datas[key]
        ret += app_data.get_vec_count()
    return ret
