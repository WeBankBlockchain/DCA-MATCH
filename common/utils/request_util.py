import requests
import json
from common.utils.log import logger

class requestsUtils:
    def post(self, url, data, header="Content-type:application/json"):
        global res
        if header == "params":
            res = requests.post(url=url, params=data)
        if header =="form-data":
            res = requests.post(url=url, data=data)
        if header=="Content-type:application/json":
            res = requests.post(url=url, json=data)
        if res.status_code != 200:
            logger.error("[http err]request url:" + url)
            raise ValueError("http returns " + str(res.status_code))
        jsonData = res.json()
        respCode = int(jsonData['responseCode'])
        if respCode != 0 and respCode != 200:
            logger.error("[server err]request url:" + url)
            raise ValueError("server returns " + str(respCode))
        return jsonData

    def get(self,url, data, header):
        global res
        if header != None:
            res = requests.get(url=url, data=data, headers=header)
        else:
            res = requests.get(url=url, data=data)
        return json.dumps(res.json(), ensure_ascii=False, sort_keys=True, indent=4)