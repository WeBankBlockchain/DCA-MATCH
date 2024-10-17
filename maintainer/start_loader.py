from maintainer.app import app_datas
from maintainer.healthy_handler import *

def start():
    dir_path = config_info.app_dir
    logger.info("maintainer disk load start...")
    ioutil.ensureFolder(dir_path)
    index_files = [os.path.join(dir_path, p) for p in sorted(os.listdir(dir_path))]
    # load info to cache
    for path in index_files:
        if path.endswith(".vec"):
            _load_vec_file(path)
        if path.endswith(".idx"):
            _load_index_file(path)

    # healthy check and fix
    for id in app_datas:
        app_data: AppStatistics = app_datas[id]
        # fix healthy problems
        _healthy_check_and_fix(app_data)

    logger.info("maintainer disk load end...")


def _load_vec_file(vec_path):
    # 从vec文件解析appId。格式:appId.vec
    app_id = ioutil.extract_appid(vec_path)
    # 读取向量文件，获取向量数目
    vec_last_pos, id_mapper = ioutil.get_vec_file_info(vec_path)
    # 初始化
    if app_id not in app_datas:
        app_datas[app_id] = AppStatistics(app_id=app_id, index=flatl2_index())
    # 设置向量数目等信息
    app_data:AppStatistics = app_datas[app_id]
    app_data.set_last_vec_pos(vec_last_pos)
    app_data.set_vec_count(len(id_mapper))
    app_data.set_prev_vec_count(len(id_mapper))

    logger.info("load vec  from {} complete.  vec last position = {} and vec count = {}".format(vec_path, vec_last_pos, len(id_mapper)))


# 获取app有多少向量
def _load_index_file(index_path):
    app_id = ioutil.extract_appid(index_path)
    # 初始化
    if app_id not in app_datas:
        app_datas[app_id] = AppStatistics(app_id=app_id, index=flatl2_index())
    app_data: AppStatistics = app_datas[app_id]
    # 加载索引数据
    index = read_index(index_path)
    app_data.set_index(index)

    logger.info(
            "load index from {}, index_type:{}, index_count:{}".format(index_path, idx_type(index), vecs_num(index)))


# 健康检测包括：类型，数目。
def _healthy_check_and_fix(app_data:AppStatistics):
    healthy = is_app_healthy(app_data)
    # 注意：这里面不能立即就决定重新构造的索引是什么类型，因为这里仍然可能文件被误删或者删除部分数据
    if not healthy:
        logger.info("app {} is not healthy, start rebuilding", app_data.get_app_id())
        rebuild_index(app_data)
        write_index(app_data.get_index(), app_data.get_index_file_path())
        logger.info("Rebuild index complete for app {}".format(app_data.get_app_id()))
        return

    logger.info("app {} is healthy, no need to rebuild".format(app_data.get_app_id()))

