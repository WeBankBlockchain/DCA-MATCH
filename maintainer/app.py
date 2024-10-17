from common.model.app_basic_info import AppBasicInfo
from common.utils import *
class AppStatistics(AppBasicInfo):

    def __init__(self, app_id, index):
        AppBasicInfo.__init__(self, app_id, index)
        # statistics
        self._vec_count = 0
        self._last_vec_pos = -1
        self._prev_vecs_count = 0 #used by healthy checker

    def get_vec_count(self)->int:
        return self._vec_count

    def set_vec_count(self, vec_cnt):
        self._vec_count = vec_cnt

    def get_last_vec_pos(self)->int:
        return self._last_vec_pos

    def set_last_vec_pos(self, pos):
        self._last_vec_pos = pos

    def get_prev_vec_count(self)->int:
        return self._prev_vecs_count

    def set_prev_vec_count(self, vec_cnt):
        self._prev_vecs_count = vec_cnt

    def reset(self):
        logger.info("truncating and resetting {}".format(self.get_app_id()))
        try:
            os.truncate(self.vec_file_path, 0)
        except:
            pass
        self._vec_count = 0
        self._last_vec_pos = -1
        self._prev_vecs_count = 0 #used by healthy checker
        self.index = flatl2_index()

app_datas = {}