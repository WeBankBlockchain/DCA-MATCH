import math
import numpy as np

def compute_cosine_distance(v1, v2):
    if len(v1) != len(v2):
        raise ValueError()
    """
    计算两个向量之间的余弦相似度
    """
    a = np.mat(v1)
    b = np.mat(v2)
    return float(a * b.T) / (np.linalg.norm(a) * np.linalg.norm(b))

# def compute_cosine_distance(v1, v2):
#     if len(v1) != len(v2):
#         raise ValueError()
#
#     product = 0
#     for i in range(len(v1)):
#         product += v1[i] * v2[i]
#
#     d1 = 0.0
#     for i in range(len(v1)):
#         d1 += math.pow(v1[i], 2)
#     d1 = math.sqrt(d1)
#
#     d2 = 0.0
#     for i in range(len(v2)):
#         d2 += math.pow(v2[i], 2)
#
#     d2 = math.sqrt(d2)
#
#     return product / (d1*d2)



# img_similarities must be sorted by descending order
def filter_if_positive(img_similarities, threshold)->(bool, list):
    if not img_similarities:
        return False, img_similarities

    top1 = img_similarities[0]['similarity']
    positive = True if top1>=threshold else False
    return positive, [img_similarities[0]] if positive else img_similarities
