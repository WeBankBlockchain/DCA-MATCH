import os
import pickle

from common.utils.log import logger
import fcntl

def ensureFolder(folder):
    try:
        os.mkdir(folder)
    except:
        pass


# /output/app1_flatL2_pca.idx

def extract_appid(path)->str:
    simpleName = path.split('/')[-1]
    splitIndex = simpleName.index('.')
    app_id = simpleName[:splitIndex]
    return app_id

def get_vec_file_info(vec_path, position=0):
    pk_id, last_pkid = 0, 0
    id_mapper = {}
    try:
        with open(vec_path, 'rb+') as f:
            f.seek(position)
            while True:
                pos = f.tell()
                try:
                    pk_id = pickle.load(f)
                    _ = pickle.load(f)
                    _ = pickle.load(f)
                    last_pkid = pk_id
                    id_mapper[pk_id] = pos
                except EOFError:
                    logger.info("load vectors from {} successfully with eof. return.".format(vec_path))
                    break
                except Exception as err:
                    logger.info("vector in {path} is damaged, truncate it:{err_info}", path=vec_path, err_info=str(err))
                    f.seek(pos)
                    f.truncate()
                    break
        return int(last_pkid), id_mapper
    except Exception as err:
        logger.info("Error opening vec file because:"+str(err))
        return -1,{}

def read_one_batch(f, batch_size):
    xids = []
    vectors = []
    ret = (xids, vectors)

    while len(xids) < batch_size:
        pos = f.tell()
        try:
            pk_id = pickle.load(f)
            _ = pickle.load(f)# file_id
            vector = pickle.load(f)
            ret[0].append(pk_id)
            ret[1].append(vector)
            if len(xids) == batch_size:
                return ret
        except EOFError:
            logger.info("meet EOF, file read complete")
            break
        except Exception as err:
            logger.info("vector is damaged, truncate it:{err_info}", err_info=str(err))
            f.seek(pos)
            f.truncate()
            break
    return ret


def read_vector_from_ssd(path, id, id_mapper):
    if id not in id_mapper:
        raise ValueError('id {} not existsin id mapper'.format(str(id)))
    position = id_mapper[id]
    with open(path, 'rb+') as f:
        f.seek(position)
        pk_id = int(pickle.load(f))
        file_id = pickle.load(f)
        loaded_vec = pickle.load(f)

        if pk_id != id:
            raise ValueError('loaded id {] != seeking id {}', str(pk_id), str(id))
        return pk_id, file_id, loaded_vec

def ensureDelete(_index_file_path):
    try:
        logger.info("Removing {file}", file=_index_file_path)
        os.remove(_index_file_path)
    except:
        pass

