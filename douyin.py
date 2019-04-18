#!/usr/bin/env python3
# encoding: utf-8
import base64
import gzip
import json
import random
from time import time
from urllib.parse import unquote_plus

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

api_endpoint_sign = "http://jokeai.zongcaihao.com/douyin/v292/sign"
api_endpoint_device = "https://jokeai.zongcaihao.com/douyin/v292/device"


def get_original_url(action, args_dict, ts, device_info):
    install_id = device_info['install_id']
    device_id = device_info['device_id']
    uuid = device_info['uuid']
    openudid = device_info['openudid']

    args = ""
    # print(args_dict)
    for (idx, val) in args_dict.items():
        args += "&{0}={1}".format(idx, val)

    url = "https://aweme.snssdk.com/aweme/" + action + "/?" \
          + args \
          + "&retry_type=no_retry&" \
          + "iid=" + str(install_id) \
          + "&device_id=" + str(device_id) \
          + "&uuid=" + str(uuid) \
          + "&openudid=" + str(openudid) \
          + "&ts=" + str(ts) \
          + "&ac=wifi&channel=wandoujia_zhiwei&aid=1128&app_name=aweme&version_code=290&version_name=2.9.0&device_platform=android&ssmix=a&device_type=ONEPLUS+A5000&device_brand=OnePlus&language=zh&os_api=28&os_version=9&manifest_version_code=290&resolution=1080*1920&dpi=420&update_version_code=2902&_rticket=1548672388498"
    return url


def get_signed_url(action, args, ts, device_info):
    original_url = get_original_url(action, args, ts, device_info)

    return sign(original_url)


def sign(original_url):
    """
    获取签名参数
    """
    data = {"url": original_url}
    resp = requests.post(url=api_endpoint_sign, data=json.dumps(data),
                         headers={"Content-Type": "application/json"}, verify=False)
    content = resp.content.decode("utf-8")
    #print(content, data)
    # exit()
    try:
        d = json.loads(content)
        if d['url'] is None:
            print(content)
        return d['url']
    except ValueError as e:
        print(e)


def api_douyin(action, args, ts, device_info):
    try:
        url = get_signed_url(action, args, ts, device_info)
        # print(url)
        # exit(0)

        resp = requests.get(url=url,
                            headers={
                                "User-Agent": "okhttp/3.10.0.1"},
                            verify=False,
                            cookies={'install_id': str(device_info['install_id'])})
        content = resp.content.decode("utf-8")
        d = json.loads(content)
        return d
    except Exception as e:
        print(e)


def get_new_device_info():
    """
    获取设备信息
    {"server_time":1555604243,"device_id":67334264811,"install_id":69771382113,"new_user":1,"said":"","openudid":"1358921046597048","android_id":"0f4c91a6de35782b","uuid":"248741956293685","iid":69771382113}

    """
    resp = requests.get(url=api_endpoint_device, verify=False)
    content = resp.content.decode("utf-8")
    try:
        d = json.loads(content)
        if d['install_id'] is None:
            print(resp)
        else:
            return d
    except Exception as e:
        print(content)
    return


# ————————————————————  APIs  ——————————————————————

# 获取用户个人粉丝数据
def api_user_posts(user_id, max_cursor):
    try:
        device_info = get_new_device_info()
        action = "v1/aweme/post"
        args = "user_id={0}&max_cursor={1}&count=10".format(user_id, max_cursor)
        ts = str(int(time()))
        data = api_douyin(action, args, ts, device_info)
        return data
    except Exception as e:
        print(e)


def wrap_api(device_info, action, args):
    try:
        ts = str(int(time()))
        data = api_douyin(action, args, ts, device_info)
        return data
    except Exception as e:
        print(e)


def request_dict(req):
    params = req.split("?")[1]
    lp = params.split('&')
    di = {}
    for e in lp:
        k, v = e.split('=')
        di[k] = unquote_plus(v)

    return dict(di)


def api_test():
    # ------------------------------------------------------------------------------------------------
    # gen device info
    device_info = get_new_device_info()
    print(device_info)
    user_id = "110725736365"
    time_now = str(int(time()))
    aweme_id = "6615981222587796743"
    # ------------------------------------------------------------------------------------------------
    # sign demo
    # sign service is for douyin android 2.9.0~3.9.0
    print(sign(
        "https://api-hl.amemv.com/aweme/v1/commit/follow/user/?user_id=60514131756&type=1&retry_type=no_retry&iid=65734914098&device_id=66679620049&ac=wifi&channel=wandoujia_zhiwei&aid=1128&app_name=aweme&version_code=290&version_name=2.9.0&device_platform=android&ssmix=a&device_type=ONEPLUS%20A6010&device_brand=OnePlus&language=zh&os_api=28&os_version=9&uuid=432635101856947&openudid=8522097096784651&manifest_version_code=290&resolution=1080*2261&dpi=420&update_version_code=2902&_rticket=1552285914901"))

    # ------------------------------------------------------------------------------------------------
    # functions wrap
    # Home feeds
    print(wrap_api(device_info, "v1/feed", {'count': 6, 'type': 0, 'max_cursor': 0, 'min_cursor': -1, 'pull_type': 2}))

    # someone's videos
    print(wrap_api(device_info, "v1/aweme/post", {"user_id": user_id, "max_cursor": 0, "count": 20}))
    # someone's likes
    print(wrap_api(device_info, "v1/aweme/favorite", {"user_id": user_id, "max_cursor": 0, "count": 20}))
    # someone's info
    print(wrap_api(device_info, "v1/user", {"user_id": user_id}))
    # someone's followings
    print(wrap_api(device_info, "v1/user/following/list", {"user_id": user_id, "count": 20, "max_time": time_now}))
    # someone's followers
    print(wrap_api(device_info, "v1/user/follower/list", {"user_id": user_id, "count": 20, "max_time": time_now}))

    # video's coments
    print(wrap_api(device_info, "v1/comment/list", {"aweme_id": aweme_id, "cursor": 0, "count": 20}))

    # ------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    # API测试
    api_test()
