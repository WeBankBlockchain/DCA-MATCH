
import json
from common.error.matcher_error import MatcherError
from common.utils.similarity_utils import compute_cosine_distance

from wm.remote import wm_store_service
from common import constants


class WmMatchManager:

    def __init__(self):
        pass

    def match(self,feature,threshold,unique_hash):
        vec= None
        uniqueId = None
        failReason = None
        positive = False
        try:
            vec,uniqueId = wm_store_service.getVectorByHash(unique_hash)
            if vec == '':
                failReason = 'vector not exist'
                return positive, 0, uniqueId, failReason
            vec = json.loads(vec)
        except Exception as e:
            raise MatcherError(code=constants.ERR_STORE_QUERY, message='error store query:' + str(e))
        cos_similarity = compute_cosine_distance(feature, vec)
        if cos_similarity < threshold:
            failReason = 'the image similarity is less than the threshold'
            return positive, cos_similarity, uniqueId, failReason
        positive = True
        return positive, cos_similarity, uniqueId, failReason

wmMatchManager = WmMatchManager()

