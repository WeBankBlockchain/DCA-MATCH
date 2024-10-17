
from maintainer.app import AppStatistics
from common.config.config import config_info
import numpy
from common.enums import *
from common.utils import *

def _deduceIndexByCount(vec_count)->IndexType:
    if vec_count < config_info.index_switch_threshold:
        return IndexType.flatL2
    return IndexType.ivfpq


# rebuild采用全部重新训练的模型。
def rebuild_index(app: AppStatistics):
    try:
        current_type = idx_type(app.get_index())
        with open(app.get_vec_file_path(), 'rb+') as f:
            logger.info("start reading from {}".format(app.get_vec_file_path()))
            do_train(f, app)
            add_remaining(f, app)
            app.set_prev_vec_count(app.get_vec_count())
            logger.info("rebuild from {fromType} to {toType} because of switch. app_id:{appId}, count:{count}",
                        fromType=current_type,
                        toType=idx_type(app.get_index()),
                        appId=app.get_app_id(),
                        count=vecs_num(app.get_index()))

    except Exception as err:
        logger.info("Rebuild failed for {} because:{}".format(app.get_app_id(), str(err)))
        errMsg = str(err)
        if errMsg == 'std::bad_alloc':
            config_info.max_train_count = max(256, config_info.max_train_count / 2)
            logger.error("Retraining {} use training count {}".format(app.get_app_id(), config_info.max_train_count))
            raise err
        # normal errors
        app.reset()

def nums_match(app: AppStatistics)->bool:
    return app.get_vec_count() == vecs_num(app.get_index())

def type_match(app: AppStatistics)->bool:
    actual_type = idx_type(app.get_index())
    expect_type = _deduceIndexByCount(app.get_vec_count())
    return actual_type == expect_type
def is_cross_thresholds(app: AppStatistics)->bool:
    before = app.get_prev_vec_count()
    after = app.get_vec_count()
    for t in config_info.retrain_threshold:
        if before < t <= after:
            return True
    return False

def is_app_healthy(app_data:AppStatistics)->bool:
    # 类型检查
    is_type_match = type_match(app_data)
    # 数目检查
    is_num_match = nums_match(app_data)
    # 训练数量检查
    not_cross_threshold = not is_cross_thresholds(app_data)
    logger.info("app {} is_type_match {} is_num_match {} not_cross_threshold {}".format(app_data.get_app_id(), is_type_match, is_num_match, not_cross_threshold))
    return is_type_match and is_num_match and not_cross_threshold


def do_train(f, app:AppStatistics):
    logger.info("start training {}",app.get_app_id())
    [xids, vectors] = ioutil.read_one_batch(f, config_info.max_train_count)
    if len(xids) == 0:
        logger.info("{file} does not exists or bad. no vectors should be loaded from vector files to index",
                    file=app.get_vec_file_path())
        app.set_vec_count(0)
        app.set_last_vec_pos(-1)
        return
    logger.info("{} {} vectors read for training".format(app.get_app_id(), len(xids)))
    vectors = numpy.array(vectors)

    index = create_index_by_type(_deduceIndexByCount(len(xids)))
    index.train(vectors)
    index.add_with_ids(vectors, xids)
    app.set_index(index)
    app.set_vec_count(len(vectors))
    app.set_last_vec_pos(xids[-1])
    logger.info("train complete. app_id:{appId}, count:{count}",
                appId=app.get_app_id(),
                count=vecs_num(index))

def add_remaining(f, app:AppStatistics):
    while True:
        [xids, vectors] = ioutil.read_one_batch(f, config_info.ssd_reload_batch)
        if len(xids) == 0:
            return
        index = app.get_index()
        vectors = numpy.array(vectors)
        index.add_with_ids(vectors, xids)
        app.set_vec_count(app.get_vec_count() + len(vectors))
        app.set_last_vec_pos(xids[-1])
        logger.info("add remaining complete. app_id:{appId}, count:{count}",
                    appId=app.get_app_id(),
                    count=vecs_num(index))