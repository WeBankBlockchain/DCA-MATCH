import os
from common.config.config import config_info
from common.utils.indexutil import flatl2_index
import faiss
# 保存app的索引、文件信息
class AppBasicInfo():

    def __init__(self, app_id, index):
        self._app_id = app_id
        self._index = index if index else flatl2_index()
        self._vec_file_path = os.path.join(config_info.app_dir, app_id+".vec")
        self._index_file_path = os.path.join(config_info.app_dir, app_id+".idx")

    def get_app_id(self) -> str:
        return self._app_id

    def set_app_id(self, app_id):
        self._app_id = app_id

    def get_index(self)->faiss.Index:
        return self._index

    def set_index(self, index):
        self._index = index

    def get_vec_file_path(self):
        return self._vec_file_path

    def get_index_file_path(self):
        return self._index_file_path
