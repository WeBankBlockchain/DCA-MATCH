import json
from common.error.matcher_error import MatcherError
from common.utils.request_util import requestsUtils
from common.config.config import config_info
from common.utils.log import logger
from common import constants

class StoreService:

    def __init__(self) -> None:
        self.requests = requestsUtils()

    def getVectorByHash(self, uniqueHash):
        response = self.requests.post(url= config_info.store_url + "/wm/getVectorByHash", data={"hash":uniqueHash})
        if 'responseData' in response and response['responseData'] is not None:
            vec = response['responseData']['feature']
            uniqueId = response['responseData']['uniqueId']
            return vec,uniqueId
        else:
            raise MatcherError(code=constants.ERR_STORE_QUERY, message='store query vec is null')

_instance = StoreService()