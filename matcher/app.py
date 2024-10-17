from common.model.app_basic_info import AppBasicInfo

class AppState(AppBasicInfo):

    def __init__(self, app_id, index, id_mapper):
        AppBasicInfo.__init__(self, app_id, index)
        self._id_mapper = id_mapper if id_mapper else {}
         # statistics
        self._vec_file_length = 0
        self._vec_last_mtime = 0
        self._index_last_mtime = 0


    def get_id_mapper(self):
        return self._id_mapper

    def set_id_mapper(self, id_mapper):
        self._id_mapper = id_mapper

    def get_vec_last_mtime(self):
        return self._vec_last_mtime

    def set_vec_last_mtime(self, time):
        self._vec_last_mtime = time

    def get_index_last_mtime(self):
        return self._index_last_mtime

    def set_index_last_mtime(self, time):
        self._index_last_mtime = time

    def set_vec_file_length(self, length):
        self._vec_file_length = length

    def get_vec_file_length(self):
        return self._vec_file_length


app_states = {}
