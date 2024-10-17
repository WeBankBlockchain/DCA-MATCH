import json
from common.utils.request_util import requestsUtils
from common.config.config import config_info
from common.utils.log import logger

class StoreService:

    def __init__(self) -> None:
        self.requests = requestsUtils()

    def getVectorsByIds(self, ids):
        response = self.requests.post(url= config_info.store_url + "/getVectorsByIds", data={"ids":ids})
        vectors = {}
        vec = []
        for item in response['responseData']:
            pk_id = item['pkId']
            file_id = item['fileId']
            vector = json.loads(item['feature'])
            vectors[pk_id] = [pk_id, file_id, vector]
        return vectors

    def getVectors(self, app_id, last_id = -1, batch = 256):
        logger.info('get vectors:{} {} {}'.format(app_id, last_id, batch))
        url = config_info.store_url + "/getVectors"
        response = self.requests.post(url=url, header="params", data={"appId":app_id,"lastId":last_id,"batch":batch})
        # print(response)

        vectors = []
        for item in response['responseData']:
            vectorObj = {}
            vectorObj['pkId'] = int(item['pkId'])
            vectorObj['fileId'] = item['fileId']
            vectorObj['feature'] = json.loads(item['feature'])

            vectors.append(vectorObj)
        vectors.sort(key=lambda x:x['pkId']) # sort by pkId
        return vectors    
        
    def getApps(self):
        url  = config_info.store_url + "/getApps"
        response = self.requests.post(url=url, data={})
        return response['responseData']

_instance = StoreService()