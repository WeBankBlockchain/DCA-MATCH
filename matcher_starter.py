#coding:UTF-8
import json
import multiprocessing

import matcher.search as manager
import threading
import schedule
from common.config.config import config_info
import time
from matcher.index_load_task import check_and_load
from flask import Flask, request, jsonify, make_response
import os
from common.remote.vc_service import _instance as vc_instance
from common.utils.log import logger
from common.utils import *
from matcher.app import app_states
from common import constants

process = multiprocessing.current_process()
# set the name
process.name = 'WaterMarkMatcherProcess_'+str(process.pid)

app = Flask(__name__)
app.logger.handlers = logger._core.handlers
app.logger.propagate = False 

local_vars = threading.local()
config = config_info
tmpDir = config.tmp_dir

basedir = os.path.abspath(os.path.dirname(__file__))  # 获取当前项目的绝对路径
local_path = threading.local()
app.config['UPLOAD_FOLDER'] = tmpDir  # 设置文件上传的目标文件夹

@app.route('/match/matchFile', methods=['POST'])
def api_matchFile():
    times = time.time()

    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])  # 拼接成合法文件夹地址
    seqNo = request.form.get('seqNo')
    app_id = request.form.get('appId')
    topK = int(request.form.get('size'))
    threshold = float(request.form.get('threshold'))

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  # 文件夹不存在就创建
    f = request.files['file']
    # 存储到本地

    local_vars.times = times
    local_vars.seqNo = seqNo

    tmpFile = f'{time.time_ns()}{os.getpid()}'
    path = os.path.join(file_dir, tmpFile)
    local_path.path=path
    f.stream.seek(0)
    f.save(path) 
    used = str(time.time() - times)
    logger.info("{} save file use time = {} ", seqNo,used)

    times = time.time()
    features = vc_instance.getFeature(path, seqNo)
    used = str(time.time() - times)
    logger.info("{} vc_instance getFeature use time = {} ", seqNo,used)

    times = time.time()
    
    positive, files = manager.search(app_id, features, topK, threshold)
    used = str(time.time() - times)
    logger.info("{} manager search use time = {} ", seqNo,used)
    res = {
        "responseCode": "000000000",
        "responseMessage": "Success",
        "responseData": {
            "positive": str(positive),
            "files": files
        }
    }
    logger.debug("positive {} {}".format(positive, type(positive)))
    rst = make_response(res)
    rst.headers['Access-Control-Allow-Origin'] = '*'
    used = str(time.time() - times)
    monitorLogs = f'{{"code": "match","bizSeqNo": "{seqNo}","resCode": "000000000","message": "Success","usedTime": {used}}}'
    logger.bind(app=True).info(monitorLogs)
    logger.info("{} succeed", seqNo)
    return rst, 200

@app.route('/match/scan', methods=['POST'])
def api_scan():
    times = time.time()

    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])  # 拼接成合法文件夹地址
    seqNo = request.form.get('seqNo')
    threshold = float(request.form.get('threshold'))
    pageNo = int(request.form.get('pageNo'))
    pageSize = int(request.form.get('pageSize'))

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  # 文件夹不存在就创建
    f = request.files['file']

    local_vars.times = times
    local_vars.seqNo = seqNo

    # 存储到本地
    tmpFile = f'{time.time_ns()}{os.getpid()}'
    path = os.path.join(file_dir, tmpFile)
    local_path.path = path
    f.stream.seek(0)
    f.save(path)
    used = str(time.time() - times)
    logger.info("{} save file use time = {} ", seqNo, used)

    times = time.time()
    features = vc_instance.getFeature(path, seqNo)
    used = str(time.time() - times)
    logger.info("{} vc_instance getFeature use time = {} ", seqNo, used)

    times = time.time()

    scan_result = manager.scan(features, threshold, pageSize, pageNo)
    used = str(time.time() - times)
    logger.info("{} manager search use time = {} ", seqNo, used)
    res = {
        "responseCode": "000000000",
        "responseMessage": "Success",
        "responseData":scan_result
    }
    rst = make_response(res)
    rst.headers['Access-Control-Allow-Origin'] = '*'
    used = str(time.time() - times)
    monitorLogs = f'{{"code": "match","bizSeqNo": "{seqNo}","resCode": "000000000","message": "Success","usedTime": {used}}}'
    logger.bind(app=True).info(monitorLogs)
    logger.info("{} succeed", seqNo)
    return rst, 200


@app.errorhandler(Exception)
def framework_error(e):
    # os.remove(local_path.path)
    error_return = {
            "responseCode": constants.ERR_INTERNAL,
            "responseMessage": "INTERNAL_ERROR"
        }
    if isinstance(e, MatcherError):
        error_return['responseCode'] = e.code
        error_return['responseMessage'] = e.message

    res = jsonify(error_return)
    rst = make_response(res)
    seqNo = local_vars.seqNo
    used = str(time.time() - local_vars.times)
    err_code = error_return['responseCode']
    err_msg = str(error_return['responseMessage']).replace('"', '').replace("'", '').replace(",", " ").replace(":", " ")
    monitorLogs = f'{{"code": "WMmatch","bizSeqNo": "{seqNo}","resCode": "{err_code}","message": "{err_msg}","usedTime": {used}}}'
    logger.bind(app=True).info(monitorLogs)
    logger.error("OnError: {}".format(e))
    logger.exception(e)
    return rst, 200

from wm.wm_match_manager import wmMatchManager


@app.route('/match/wm/auth', methods=['POST'])
def api_wm_match():
    times = time.time()
    seqNo = request.form.get('seqNo')
    unique_hash = request.form.get('uniqueHash')
    threshold = float(request.form.get('threshold'))
    f = request.files['file'].read()
    local_vars.times = times
    local_vars.seqNo = seqNo
    features = vc_instance.getFeatureByStream(f, seqNo)
    used = str(time.time() - times)
    logger.info("{} vc_instance getFeature use time = {} ", seqNo, used)

    times = time.time()
    positive, cos_similarity,uniqueId,failReason = wmMatchManager.match(features, threshold, unique_hash)
    used = str(time.time() - times)
    res = {
        "responseCode": "000000000",
        "responseMessage": "Success",
        "responseData": {
            "positive": str(positive),
            "similarity": cos_similarity,
            "uniqueId" : uniqueId,
            "failReason" : failReason
        }
    }
    logger.info("tx [{}] wmMatchManager match use time = [{}], threshold = [{}], res = [{}]", seqNo,used, str(threshold), res)
    rst = make_response(res)
    rst.headers['Access-Control-Allow-Origin'] = '*'
    used = str(time.time() - local_vars.times)
    monitorLogs = f'{{"code": "WMmatch","bizSeqNo": "{seqNo}","resCode": "000000000","message": "Success","usedTime": {used}}}'
    logger.bind(app=True).info(monitorLogs)
    return rst, 200

def tasklist():
    #清空任务
    schedule.clear()
    #创建一个按秒间隔执行任务
    schedule.every(config_info.index_load_interval_seconds).seconds.do(check_and_load)
    while True:
        schedule.run_pending()
        time.sleep(1)

def startTasks():
    thread = threading.Thread(target=tasklist)
    thread.start()
#
#

# 磁盘加载
# check_and_load()
# 启动定时任务
# startTasks()

if __name__ == '__main__':
    logger.debug("started")
    # 磁盘加载
    # check_and_load()
    # 启动定时任务
    # startTasks()
    # 启动网站
    app.run(port=int(config.port))
    # #

    # print(res)
    # #
