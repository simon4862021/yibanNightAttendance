# -*- coding: utf-8 -*-
import requests
import json
import re
import time
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

# 代码部分参考自https://hub.fastgit.org/rookiesmile/yibanAutoSgin
class Yiban:
    CSRF = "64b5c616dc98779ee59733e63de00dd5"
    COOKIES = {"csrf_token": CSRF}
    HEADERS = {
        'Origin': 'https://mobile.yiban.cn',
        'User-Agent': 'YiBan/5.0.1 Mozilla/5.0 (Linux; Android 7.1.2; V1938T Build/N2G48C; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Safari/537.36',
        'Referer': 'https://mobile.yiban.cn',
        'AppVersion': '5.0.1'}
    EMAIL = {}
    
    def __init__(self, mobile, password):
        self.mobile = mobile
        self.password = password
        self.session = requests.session()
        # 从https://lbs.amap.com/tools/picker 寻找宿舍经纬度
        LNGLAT=os.environ["LNGLAT"]
        ADDRESS=os.environ["ADDRESS"]
        self.night_sgin ='{"Reason":"","AttachmentFileName":"","LngLat":"%s","Address":"%s"}' %(LNGLAT,ADDRESS)
        
    def request(self, url, method="get", params=None, cookies=None):
        if method == "get":
            try:
                response= self.session.get(url=url, timeout=10, headers=self.HEADERS, params=params, cookies=cookies)
            except requests.exceptions.Timeout as e:
                print("连接超时")
            except requests.exceptions.ConnectionError as e:
                print("网络异常")
            except requests.exceptions.HTTPError as e:
                print("返回了不成功的状态码")
            except Exception as e:
                print("出现了意料之外的错误")
                print(str(e))
        else:
            try:
                response = self.session.post(url=url, timeout=10, headers=self.HEADERS, data=params, cookies=cookies)
            except requests.exceptions.Timeout as e:
                print("连接超时")
            except requests.exceptions.ConnectionError as e:
                print("网络异常")
            except requests.exceptions.HTTPError as e:
                print("返回了不成功的状态码")
            except Exception as e:
                print("出现了意料之外的错误")
                print(str(e))
        return response.json()
    
    def encryptPassword(self, pwd):
        #密码加密
        PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
            MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA6aTDM8BhCS8O0wlx2KzA
            Ajffez4G4A/QSnn1ZDuvLRbKBHm0vVBtBhD03QUnnHXvqigsOOwr4onUeNljegIC
            XC9h5exLFidQVB58MBjItMA81YVlZKBY9zth1neHeRTWlFTCx+WasvbS0HuYpF8+
            KPl7LJPjtI4XAAOLBntQGnPwCX2Ff/LgwqkZbOrHHkN444iLmViCXxNUDUMUR9bP
            A9/I5kwfyZ/mM5m8+IPhSXZ0f2uw1WLov1P4aeKkaaKCf5eL3n7/2vgq7kw2qSmR
            AGBZzW45PsjOEvygXFOy2n7AXL9nHogDiMdbe4aY2VT70sl0ccc4uvVOvVBMinOp
            d2rEpX0/8YE0dRXxukrM7i+r6lWy1lSKbP+0tQxQHNa/Cjg5W3uU+W9YmNUFc1w/
            7QT4SZrnRBEo++Xf9D3YNaOCFZXhy63IpY4eTQCJFQcXdnRbTXEdC3CtWNd7SV/h
            mfJYekb3GEV+10xLOvpe/+tCTeCDpFDJP6UuzLXBBADL2oV3D56hYlOlscjBokNU
            AYYlWgfwA91NjDsWW9mwapm/eLs4FNyH0JcMFTWH9dnl8B7PCUra/Lg/IVv6HkFE
            uCL7hVXGMbw2BZuCIC2VG1ZQ6QD64X8g5zL+HDsusQDbEJV2ZtojalTIjpxMksbR
            ZRsH+P3+NNOZOEwUdjJUAx8CAwEAAQ==
            -----END PUBLIC KEY-----'''
        cipher = PKCS1_v1_5.new(RSA.importKey(PUBLIC_KEY))
        cipher_text = base64.b64encode(cipher.encrypt(bytes(pwd, encoding="utf8")))
        return cipher_text.decode("utf-8")
    
    def login(self):
        params = {
            "mobile": self.mobile,
            "password": self.encryptPassword(self.password),
            "ct": "2",
            "identify": "0",
        }
        # 新的登录接口
        response = self.request("https://mobile.yiban.cn/api/v4/passport/login", method="post", params=params,cookies=self.COOKIES)
        if response is not None and response["response"] == 100:
            self.access_token = response["data"]["access_token"]
            self.HEADERS["Authorization"] = "Bearer " + self.access_token
            # 增加cookie
            self.COOKIES["loginToken"] = self.access_token
            return response
        else:
            return response
        
    def auth(self) -> json:
#         location = self.session.get("http://f.yiban.cn/iapp7463" + "?v_time=" + str(int(round(time.time() * 100000))))
#         act = self.session.get("https://f.yiban.cn/iapp/index?act=iapp7463", allow_redirects=False, cookies=self.COOKIES)
        act = self.session.get("https://f.yiban.cn/iapp/index", allow_redirects=False, cookies=self.COOKIES)
        print("act:",act.headers)
        verifyRequest = re.findall(r"verify_request=(.*?)&",act.headers['Location'])[0]
        self.HEADERS.update({
            'origin': 'https://app.uyiban.com',
            'referer': 'https://app.uyiban.com/',
            'Host': 'api.uyiban.com',
            'user-agent': 'yiban'
        })
        response = self.request(
            "https://api.uyiban.com/base/c/auth/yiban?verifyRequest=" + verifyRequest + "&CSRF=" + self.CSRF,
            cookies=self.COOKIES)
        self.name = response["data"]["PersonName"]
        return response

    def deviceState(self):
        response=self.request(url="https://api.uyiban.com/nightAttendance/student/index/deviceState?CSRF=" + self.CSRF,
                            cookies=self.COOKIES)
        response=json.loads(response.text)
        return response

    def sginPostion(self):
        response=self.request(url="https://api.uyiban.com/nightAttendance/student/index/signPosition?CSRF=" + self.CSRF,
                            cookies=self.COOKIES)
        response=json.loads(response.text)
        return response
    
    def nightAttendance(self, reason) -> json:
        params = {
            "Code": "",
            "PhoneModel": "",
            "SignInfo": reason,
            "OutState": "1"
        }
        response = self.request("https://api.uyiban.com/nightAttendance/student/index/signIn?CSRF=" + self.CSRF,
                                method="post", params=params, cookies=self.COOKIES)
        return response
        
    def setall(self):
        self.login()
        self.auth()
        self.deviceState()
        time.sleep(1)
        self.sginPostion()
        time.sleep(1)
        status = self.nightAttendance(self.night_sgin)
        return status

def main():
    # 修改下方的手机号和密码，即可实现一个宿舍一起签到
    MOBILE=os.environ["MOBILE"]
    PASSWORD=os.environ["PASSWORD"]
    a = Yiban(MOBILE, PASSWORD)
#    b = Yiban("moblie", "password")
#    c = Yiban("moblie", "password")
#    d = Yiban("moblie", "password")
    yb_list = [a]
    for i in range(len(yb_list)):
        status = yb_list[i].setall()
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print(status)
        if status["code"] == 0:
            print("位置签到提交成功！")
        else:
            print("失败！")
            break
        time.sleep(1)
    
if __name__ == '__main__':
    main()
    
