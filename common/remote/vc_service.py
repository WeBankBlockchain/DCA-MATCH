from io import BytesIO
import json
import logging

from common.utils.request_util import requestsUtils
from common.config.config import config_info
import threading
from uuid import uuid1
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
from common.error import *
from common import constants
from common.utils.time_consumer import timeConsumer

class VcService():

    def __init__(self) -> None:
        self.requests = requestsUtils()

    @timeConsumer("getFeature")
    def getFeature(self, f,seqNo):
        try:
            boundary = '----' + str(uuid1())
            headers = {
                'Content-Length': str(os.path.getsize(f)),
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'multipart/form-data; boundary=' + boundary,
            }
            url = config_info.vc_url + "/compute/feature"
            binary_io = open(f, 'rb')

            img_data = MultipartEncoder(fields={
                'seqNo': str(seqNo),
                'file': (os.path.basename(f), binary_io, format)}, boundary=boundary, encoding='utf-8')
            result = requests.post(url=url, data=img_data, headers=headers).json()
            if result['responseCode'] != '0':
                raise ValueError('server responses '+ str(result['responseCode']))
            return json.loads(result['vector'])
        except Exception as e:
            raise MatcherError(code=constants.ERR_COMPUTE_VECTOR, message='error compute vector:'+str(e))

    def getFeatureByStream(self, f,seqNo):
        try:
            boundary = '----' + str(uuid1())
            headers = {
                'Content-Type': 'multipart/form-data; boundary=' + boundary
            }
            url = config_info.vc_url + "/compute/feature"
            img_data = MultipartEncoder(fields={
                'seqNo': str(seqNo),
                'file': ('img',f, format)}, boundary=boundary, encoding='utf-8')
            result = requests.post(url=url, data=img_data, headers=headers).json()
            if result['responseCode'] != '0':
                raise ValueError('server responses '+ str(result['responseCode']))
            return json.loads(result['vector'])
        except Exception as e:
            raise MatcherError(code=constants.ERR_COMPUTE_VECTOR, message='error compute vector:'+str(e))



_instance = VcService()
