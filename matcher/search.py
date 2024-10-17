import time
from matcher.app import AppState, app_states
from common.error.matcher_error import MatcherError

import numpy
from common.utils.log import logger
from common import remote, constants, utils as ioutil

from common.utils.similarity_utils import *



def search( app_id, qvec, topk=10, threshold=0.99):
    if app_id not in app_states:
        raise MatcherError(code=constants.ERR_APP_NOT_FOUND,message='no app id:'+app_id)
    # 搜索
    img_similarities = _search(app_id, qvec, topk)
    # 按照相似度递减排序
    sorted_similarities = sorted(img_similarities, key=lambda x: x['similarity'], reverse=True)
    # 判断是否判断为阳性
    positive, filtered_similarities = filter_if_positive(sorted_similarities, threshold)
    return positive, filtered_similarities

def scan(features, threshold, pageSize, pageNo):
    files = []
    for app_id in app_states:
        img_similarities = _search(app_id, features, topk=50)
        files += img_similarities


    filtered = []
    for item in files:
        if item['similarity'] >= threshold:
            filtered.append(item)

    filtered = sorted(filtered, key=lambda x: x['similarity'], reverse=True)

    start_index = (pageNo-1)*pageSize
    end_index = min(pageNo*pageSize, len(filtered))

    ret_files = filtered[start_index:end_index] if start_index < len(filtered) else []
    return {
        'totalCount': str(len(filtered)),
        'files':ret_files
    }
def _search( app_id, qvec, topk=10):
    indexWrapper:AppState = app_states[app_id]
    # 在索引内搜索
    query = numpy.array([qvec])
    times = time.time()
    D, I = indexWrapper.get_index().search(query, topk)
    used = str(time.time() - times)
    logger.info("indexWrapper get_index  search use time = {} ",used)

    times = time.time()
    # 先尝试通过磁盘获取向量
    vecs = read_vectors_from_local(I[0], indexWrapper.get_vec_file_path(), indexWrapper.get_id_mapper())
    used = str(time.time() - times)
    logger.info("read_vectors_from_local use time = {} ",used)
    # 若存在缺失，则尝试从storeservice拉过去
    if len(vecs) < len(I[0]):
        missing_vector_ids = _missing_vector_ids(I[0], vecs)
        logger.warning("{} read missing vectors from remote:{} vs {}".format(app_id, I[0], vecs))
        remote_vecs = remote.store_service_stub.getVectorsByIds(missing_vector_ids) if missing_vector_ids else{}
        vecs = {**vecs, **remote_vecs}
    times = time.time()
    # 计算相似度
    img_similarities = compute_similarities(qvec, vecs)
    used = str(time.time() - times)
    logger.info("compute_similarities use time = {} ",used)
    return img_similarities


def read_vectors_from_local(idlist, vec_path, id_mapper):
    founded_vecs = {}
    for id in idlist:
        if id == -1:
            continue
        try:
            pk_id, file_id, vec = ioutil.read_vector_from_ssd(vec_path, id, id_mapper)
            founded_vecs[id] = [pk_id, file_id, vec]
        except Exception as err:
            logger.warning("id {id} not found int {path}: {err}",
                        id=id,
                        path=vec_path,
                        err=str(err))

    return founded_vecs


def _missing_vector_ids(ids, local_vecs):
    ret = []
    for id in ids:
        if id == -1 or id in local_vecs:
            continue
        ret.append(str(id))
    return ret

def compute_similarities(vector, vecs:dict):
    img_similarity = []
    for id in vecs:
        result_vector = vecs[id]
        pk_id = result_vector[0]
        file_id = result_vector[1]
        feature = result_vector[2]

        cos_similarity = compute_cosine_distance(feature, vector)
        img_similarity.append(
            {
             'fileId':file_id,
             'similarity':cos_similarity})
    return img_similarity
