# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import io
import six
import cv2
import time
import json 
import random
import urllib2
import requests
import traceback
import numpy as np

from tornado import gen
from tornado import escape
from datetime import datetime
from contextlib import closing
from tornado.httputil import url_concat
from tornado.httpclient import HTTPRequest
from tornado.httpclient import AsyncHTTPClient


class ZIMGException(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value
    def __str__(self):
        return self.value

def upload_img(zimg_url,img):
    # print "img_server_url: ",zimg_url
    # print "img type:",type(img)
    # print "cv2.version:",cv2.__version__
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    _,b = cv2.imencode('.jpg',img)
    #img = img.astype(np.uint8)
    # img = np.fromstring(img,dtype="uint8")
    # img = cv2.imdecode(img, 1)
    # print "b.type",b
    data = bytearray(b)
    # print "data type: ",type(data)
    try:
        req = urllib2.Request(zimg_url, data)

        req.add_header('Content-Type','image/jpeg')
        resp = urllib2.urlopen(req, timeout=5)
        qrcont = resp.read()
        # print "qrcont:",qrcont
        qrcont = json.loads(qrcont)
        str_full_md5 = str(qrcont['info']['md5'])
        return str_full_md5
    except Exception as e:
        print("upload img error {}".format(e))
        raise ZIMGException("cannot upload img to the image server")

def idcode_age(idcode):
    """ 身份证号码转年龄 """
    year_now = int(time.strftime("%Y",time.localtime()))
    userbirth = year_now
    if len(idcode) == 15:
        userbirth = int("19"+idcode[6:8])
    elif len(idcode) == 18:
        userbirth = int(idcode[6:10])
    else:
        return ""
    return str(year_now - userbirth)

def md5_get_img_old(md5):
    try:
        st = time.time()
        imgurl = "http://192.168.5.136:48069/%s?p=0"%md5
        #imgurl = "https://security.0easy.com/img/%s?p=0"%md5
        #with closing(requests.get(imgurl, timeout=(1,3), stream=True)) as req:
        '''
        req = requests.get(imgurl)
        print req.headers
        print time.time() - st
        imgstr = req.text.encode("utf-8")
        '''
        re = urllib2.urlopen(imgurl,timeout=20)
        # "re.headers",re.info()
        imgstr = re.read()
        print ("get img from zimg time : {:.3f}s".format(time.time() - st))
        img = cv2.imdecode(np.fromstring(imgstr,np.uint8), cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # print img
        return img
    except Exception as e:
        # print req.headers
        print ("cannot get image from image server!")
        raise ZIMGException("cannot get image from image server!")

@gen.coroutine
def url_get_img(url):
    http_client = AsyncHTTPClient()
    rqt = pack_request(url, "GET")
    response = yield http_client.fetch(rqt)
    if response.error:
        raise ZIMGException("cannot get img from the url")
    else:
        img = cv2.imdecode(np.fromstring(response.body,np.uint8), cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        raise gen.Return(img)


def url_get_img_syn(url):
    r = requests.get(url)
    img = cv2.imdecode(np.fromstring(r.content, np.uint8), cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


@gen.coroutine
def md5_get_img(md5):
    imgurl = "http://192.168.5.136:48069/{}?p=0".format(md5)
    http_client = AsyncHTTPClient()
    rqt = pack_request(imgurl, "GET")
    response = yield http_client.fetch(rqt)
    if response.error:
        raise ZIMGException(response.error)
    else:
        img = cv2.imdecode(np.fromstring(response.body,np.uint8), cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        raise gen.Return(img)

def jaccard_with_anchors(face_axis, car_axis):
    new_car_axis = []
    for (xmin_0,ymin_0,xmax_0,ymax_0) in car_axis:
        flag = True
        for (xmin_1, ymin_1, xmax_1, ymax_1) in face_axis:
            int_xmin = np.max((xmin_0,xmin_1))
            int_ymin = np.max((ymin_0,ymin_1))
            int_xmax = np.min((xmax_0,xmax_1))
            int_ymax = np.min((ymax_0,ymax_1))
            h = np.maximum(int_ymax - int_ymin, 0)
            w = np.maximum(int_xmax - int_xmin, 0)
            inter_vol = h * w
            union_vol = ((ymax_1 - ymin_1) * (xmax_1 - xmin_1) - h * w) + (xmax_1 - xmin_1) * (ymax_1 - ymin_1)
            jaccard = inter_vol * 1.0 / union_vol
            if jaccard > 0.5:
                flag = False
                continue
        if flag:
            new_car_axis.append((xmin_0,ymin_0,xmax_0,ymax_0))
    return new_car_axis



def datetime_toString(dt):
    return dt.strftime("%Y-%m-%d")

#把字符串转成datetime
def string_toDatetime(string):
    return datetime.strptime(string, "%Y-%m-%d %X")

#把字符串转成时间戳形式
def string_toTimestamp(strTime):
    return time.mktime(string_toDatetime(strTime).timetuple())

#把时间戳转成字符串形式
def timestamp_toString(stamp):
    return time.strftime("%Y-%m-%d-%H", tiem.localtime(stamp))

#把datetime类型转外时间戳形式
def datetime_toTimestamp(dateTim):
    return time.mktime(dateTim.timetuple())

@gen.coroutine
def async_request(rqt):
    result=dict()
    http_client = AsyncHTTPClient()
    response    = yield http_client.fetch(rqt)
    # print 'the response is:\n',response.body
    # print '\n'
    if response.error:
        print("Error:", response.error)
    else:
        # print response.body
        result =escape.json_decode(response.body)
    # print "the result is",result
    raise gen.Return(result) 

def pack_request(url,method,**kwargs):
    body = ""
    if isinstance(kwargs, dict):
        body = json.dumps(kwargs, ensure_ascii=False)
        if isinstance(body, six.text_type):
            body = body.encode('utf8')
    #     kwargs["data"] = body
    if method.upper()=='GET':
        url=url_concat(url,kwargs)
        body=None
    # elif method=='post':
    #     url=url_concat(url,kwargs['params'])
    #     body =kwargs['data']
    # print "@@@@the body is",body
    rqt=HTTPRequest( 
                url=url, 
                method=method.upper(), 
                body=body,
                )
    return rqt

def response_wrapper(func):
    def wrapper(*args,**kwargs):
        return func(*args,**kwargs)
        
    return wrapper

def totext(value, encoding='utf-8'):
    """将 value 转为 unicode，默认编码 utf-8

    :param value: 待转换的值
    :param encoding: 编码
    """
    if not value:
        return ''
    if isinstance(value, six.text_type):
        return value
    if isinstance(value, six.binary_type):
        return value.decode(encoding)
    return six.text_type(value)


def tobinary(value, encoding='utf-8'):
    """将 values 转为 bytes，默认编码 utf-8

    :param value: 待转换的值
    :param encoding: 编码
    """
    if not value:
        return b''
    if isinstance(value, six.binary_type):
        return value
    if isinstance(value, six.text_type):
        return value.encode(encoding)

    if six.PY3:
        return six.binary_type(str(value), encoding)  # For Python 3
    return six.binary_type(value)


def disable_urllib3_warning():
    """
    https://urllib3.readthedocs.org/en/latest/security.html#insecurerequestwarning
    InsecurePlatformWarning 警告的临时解决方案
    """
    try:
        import requests.packages.urllib3
        requests.packages.urllib3.disable_warnings()
    except Exception:
        pass


def generate_timestamp():
    """生成 timestamp
    :return: timestamp string
    """
    return int(time.time())


def generate_nonce():
    """生成 nonce
    :return: nonce string
    """
    return random.randrange(1000000000, 2000000000)

if __name__ == '__main__':
    main()
