from flask import Flask, render_template, make_response
import os
from flask import request
import hashlib
import requests
import json
import logging
import time

app = Flask(__name__)

appid = "wxd315dbdf94f065f3"
appsecret = "fd115dc3a2603d5c92772b7a6aa3540f"


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('test.html', testflag="testflag")


@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    #GET方法为验证请求
    '''
        method： 起始行，元数据
        host： 起始行，元数据
        path： 起始行，元数据
        environ： 其中的 SERVER_PROTOCOL 是起始行，元数据
        headers： 头，元数据
        data： body， 元数据
        remote_addr： 客户端地址
        args： 请求链接中的参数（GET 参数），解析后
        form： form 提交中的参数，解析后
        values： args 和 forms 的集合
        json： json 格式的 body 数据，解析后
        cookies： 指向 Cookie 的链接
        '''
    if request.method == 'GET':
        token = 'huchangyi'
        data = request.args
        signature = data.get('signature', '')
        timestamp = data.get('timestamp', '')
        nonce = data.get('nonce', '')
        echostr = data.get('echostr', '')
        s = [timestamp, nonce, token]
        s.sort()
        s = ''.join(s)
        s = s.encode()
        if(hashlib.sha1(s).hexdigest() == signature):
            return make_response(echostr)
        else:
            return make_response("error")
    #用户发送的数据会使用POST方法
    elif request.method == 'POST':
        from xml.etree import ElementTree
        xml = ElementTree.fromstring(request.data)
        ToUserName = xml.find("ToUserName").text
        FromUserName = xml.find("FromUserName").text
        MsgType = xml.find("MsgType").text
        if(MsgType == "text"):
            Content = "已收到文本消息：" + xml.find("Content").text
        elif (MsgType == "image"):
            Content = "收到图片消息"
        elif (MsgType == "voice"):
            Content = "收到语音消息"
        elif (MsgType == "video"):
            Content = "收到视频消息"
        elif (MsgType == "shortvideo"):
            Content = "收到小视频消息"
        elif (MsgType == "location"):
            Content = "收到地理位置消息"
        elif (MsgType == "link"):
            Content = "收到链接消息"
        reply = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"
        app.logger.info("开发者微信号:" + FromUserName + "发送方帐号:" + ToUserName + "文本消息内容:" + Content)
        response = make_response(
            reply % (FromUserName, ToUserName, str(int(time.time())), Content))
        response.content_type = 'application/xml'
        return response
    else:
        return None



@app.route('/wechat_test', methods=['GET', 'POST'])
def wechat_test():
    getString = "http://flask.huchangyi.com/wechat?signature=789bbf0fc5406791e882c7720ebaf352dba6d3b4&echostr=16320267320662293951&timestamp=1527643317&nonce=1129712787"
    testflag = requests.get(getString).text
    return render_template('test.html', testflag=testflag)
    '''
    post
    payload = {'key1': 'value1', 'key2': 'value2'}
    r = requests.post("http://httpbin.org/post", data=payload)
    print r.text
    认证
    url = 'http://localhost:8080'
    r = requests.post(url, data={}, auth=HTTPBasicAuth('admin', 'admin'))
    print r.status_code
    print r.headers
    print r.reason
    '''


@app.route('/get_access_token', methods=['GET', 'POST'])
def get_access_token():
    getString = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + appid + "&secret=" + appsecret
    jsonString = requests.get(getString).text
    #jsonDump = json.dumps(jsonString)
    #jsonData = json.loads(jsonDump)
    jsonData = eval(jsonString)
    access_token = jsonData['access_token']
    return access_token


@app.route('/create_menu', methods=['GET', 'POST'])
def create_menu():
    access_token = get_access_token()
    postUrl = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=" + access_token
    postData = {
    "button": [
        {
            "type": "click",
            "name": "点击获取",
            "key": "v001"
        },
        {
            "name": "功能菜单",
            "sub_button": [
                {
                    "type": "view",
                    "name": "我的网站",
                    "url": "http://www.huchangyi.com/"
                },
                {
                    "type": "click",
                    "name": "赞一下我们",
                    "key": "v002"
                }
            ]
        }
    ]
    }
    postData = json.dumps(postData, ensure_ascii=False).encode('utf-8')
    resString = requests.post(postUrl, data=postData).text
    return resString


@app.route('/get_menu', methods=['GET', 'POST'])
def get_menu():
    access_token = get_access_token()
    getUrl = "https://api.weixin.qq.com/cgi-bin/menu/get?access_token=" + access_token
    resString = requests.get(getUrl).text
    return resString


@app.route('/delete_menu', methods=['GET', 'POST'])
def delete_menu():
    access_token = get_access_token()
    getUrl = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=" + access_token
    resString = requests.get(getUrl).text
    return resString


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='flask.log',
                        filemode='w')
    app.run(
        app.run(host="0.0.0.0", port=80)
    )

