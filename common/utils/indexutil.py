import os

import faiss
from common.enums.index_type import IndexType
from common.utils.log import logger
from common.error import MatcherError
from common import error
from common.constants import *
import fcntl

def idx_type(index)->IndexType:
    if not index:
        raise error.MatcherError(code=ERR_NONE_INDEX, message='none index')

    type_name = index.__class__.__name__
    if type_name == 'IndexIDMap2':
        return IndexType.flatL2
    elif type_name == 'IndexIVFPQ':
        return IndexType.ivfpq
    else:
        raise error.MatcherError(code=ERR_INVALID_INDEX_TYPE, message="unknown type name:" + type_name)


def vecs_num(index)->int:
    return index.ntotal

def read_index(path:str):
    index = None
    with open(path+".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        try:
            index = faiss.read_index(path)
        except Exception as err:
            logger.error("error load {} due to err {}. Use dummy index".format(path, str(err)))
            index = flatl2_index()
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
    logger.info("index from {} has {} vectors".format(path, index.ntotal))
    return index

def write_index(index, path):

     # 假设进程A在读index，进程B此时先写入tmp文件，最后一步再替换，这样效率高很多
    with open(path+".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            faiss.write_index(index, path)
        except Exception as err:
            logger.warning("error write {} due to err {}.".format(path, str(err)))
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def flatl2_index():
    index = faiss.IndexFlatL2(DIMENSIONS)
    index = faiss.IndexIDMap2(index)
    return index

def ivfpq_index():
    quantizer = faiss.IndexFlatL2(DIMENSIONS)  # this remains the same
    index = faiss.IndexIVFPQ(quantizer, DIMENSIONS, IVFPQ_NLIST, IVFPQ_M, IVFPQ_K)
    index.nprobe = IVFPQ_NPROBE
    return index

def create_index_by_type(type:IndexType):
    if type == IndexType.flatL2:
        return flatl2_index()
    elif type==IndexType.ivfpq:
        return ivfpq_index()
    raise MatcherError(code=ERR_INVALID_INDEX_TYPE, message="unknown type name:" + type)