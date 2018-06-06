from flask import Flask, render_template, make_response, redirect
import os
from flask import request
import hashlib
import requests
import json
import logging
import time
import urllib
import pymysql
import datetime

app = Flask(__name__)

appid = "wxd315dbdf94f065f3"
appsecret = "fd115dc3a2603d5c92772b7a6aa3540f"

mini_appid = "wxe8fd6407da9c0206"
mini_appsecret = "7de8b05401486a7963de7975d117f5a"


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('test.html', testflag="testflag")


@app.route('/wechat/', methods=['GET', 'POST'])
def wechat():
    """
    get方法为验证请求
    post方法为所有消息事件
    request.
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
    :return: 返回给微信的验证
    """
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
    elif request.method == 'POST':
        from xml.etree import ElementTree
        xml = ElementTree.fromstring(request.data)
        ToUserName = xml.find("ToUserName").text
        FromUserName = xml.find("FromUserName").text
        MsgType = xml.find("MsgType").text
        #用户消息事件推送
        if(MsgType == "text"):
            Content = "收到文本消息：" + xml.find("Content").text
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
        #自定义菜单事件推送
        elif (MsgType == "event"):
            Event = xml.find("Event").text
            if(Event == "CLICK"):
                Content = "点击菜单拉取的事件"
            elif (Event == "VIEW"):
                Content = "点击菜单跳转链接的事件"
            elif (Event == "scancode_push"):
                Content = "扫码推事件"
            elif (Event == "scancode_waitmsg"):
                Content = "扫码推事件且弹出消息接收中的事件"
            elif (Event == "pic_sysphoto"):
                Content = "弹出系统拍照发图的事件"
            elif (Event == "pic_photo_or_album"):
                Content = "弹出拍照或者相册发图的事件"
            elif (Event == "pic_weixin"):
                Content = "弹出微信相册发图器的事件"
            elif (Event == "location_select"):
                Content = "弹出地理位置选择器的事件"
        reply = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"
        app.logger.info("开发者微信号:" + FromUserName + "发送方帐号:" + ToUserName + "文本消息内容:" + Content)
        response = make_response(
            reply % (FromUserName, ToUserName, str(int(time.time())), Content))
        response.content_type = 'application/xml'
        return response
    else:
        return None


@app.route('/test/', methods=['GET', 'POST'])
def test():
    nowtime = datetime.datetime.now()
    db = pymysql.connect("qdm165067450.my3w.com", "qdm165067450", "huchangyi", "qdm165067450_db")
    cursor = db.cursor()
    cursor.execute("select * from access_token order by time desc limit 1")
    data = cursor.fetchone()
    lasttime = data[2]
    db.close()
    try:
        lasttime = datetime.datetime.strptime(lasttime, "%Y-%m-%d %H:%M:%S.%f")
    except:
        lasttime = datetime.datetime.strptime(lasttime, "%Y-%m-%d-%H")
    if(nowtime-lasttime>datetime.timedelta(minutes=120) ):
        getString = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" \
                    + appid + "&secret=" + appsecret
        jsonString = requests.get(getString).text
        # jsonDump = json.dumps(jsonString)
        # jsonData = json.loads(jsonDump)
        jsonData = eval(jsonString)
        access_token = jsonData['access_token']
        db = pymysql.connect("qdm165067450.my3w.com", "qdm165067450", "huchangyi", "qdm165067450_db")
        cursor = db.cursor()
        try:
            sql = "update access_token set token = '" + access_token + "', time = '"\
                           + str(nowtime) + "' where id = 1"
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
        db.close()
        return access_token
    else:
        return data[0]


@app.route('/get_access_token/', methods=['GET', 'POST'])
def get_access_token():
    """
    根据公共变量appid和appsecret获取access_token
    :return:
    """




    getString = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + appid + "&secret=" + appsecret
    jsonString = requests.get(getString).text
    #jsonDump = json.dumps(jsonString)
    #jsonData = json.loads(jsonDump)
    jsonData = eval(jsonString)
    access_token = jsonData['access_token']
    return access_token


@app.route('/create_menu/', methods=['GET', 'POST'])
def create_menu():
    """
    1、click：点击推事件用户点击click类型按钮后，微信服务器会通过消息接口推送消息类型为event的结构给开发者（参考消息接口指南），并且带上按钮中开发者填写的key值，开发者可以通过自定义的key值与用户进行交互；
    2、view：跳转URL用户点击view类型按钮后，微信客户端将会打开开发者在按钮中填写的网页URL，可与网页授权获取用户基本信息接口结合，获得用户基本信息。
    3、scancode_push：扫码推事件用户点击按钮后，微信客户端将调起扫一扫工具，完成扫码操作后显示扫描结果（如果是URL，将进入URL），且会将扫码的结果传给开发者，开发者可以下发消息。
    4、scancode_waitmsg：扫码推事件且弹出“消息接收中”提示框用户点击按钮后，微信客户端将调起扫一扫工具，完成扫码操作后，将扫码的结果传给开发者，同时收起扫一扫工具，然后弹出“消息接收中”提示框，随后可能会收到开发者下发的消息。
    5、pic_sysphoto：弹出系统拍照发图用户点击按钮后，微信客户端将调起系统相机，完成拍照操作后，会将拍摄的相片发送给开发者，并推送事件给开发者，同时收起系统相机，随后可能会收到开发者下发的消息。
    6、pic_photo_or_album：弹出拍照或者相册发图用户点击按钮后，微信客户端将弹出选择器供用户选择“拍照”或者“从手机相册选择”。用户选择后即走其他两种流程。
    7、pic_weixin：弹出微信相册发图器用户点击按钮后，微信客户端将调起微信相册，完成选择操作后，将选择的相片发送给开发者的服务器，并推送事件给开发者，同时收起相册，随后可能会收到开发者下发的消息。
    8、location_select：弹出地理位置选择器用户点击按钮后，微信客户端将调起地理位置选择工具，完成选择操作后，将选择的地理位置发送给开发者的服务器，同时收起位置选择工具，随后可能会收到开发者下发的消息。
    9、media_id：下发消息（除文本消息）用户点击media_id类型按钮后，微信服务器会将开发者填写的永久素材id对应的素材下发给用户，永久素材类型可以是图片、音频、视频、图文消息。请注意：永久素材id必须是在“素材管理/新增永久素材”接口上传后获得的合法id。
    10、view_limited：跳转图文消息URL用户点击view_limited类型按钮后，微信客户端将打开开发者在按钮中填写的永久素材id对应的图文消息URL，永久素材类型只支持图文消息。请注意：永久素材id必须是在“素材管理/新增永久素材”接口上传后获得的合法id。
    {
        "type": "media_id",
        "name": "下发消息",
        "key": "media_id"
    }
    {
        "type": "view_limited",
        "name": "跳转图文",
        "key": "view_limited"
    }
    """
    access_token = get_access_token()
    postUrl = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=" + access_token
    postData = {
    "button": [
        {
            "type": "view",
            "name": "网页",
            "url": "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxd315dbdf94f065f3&redirect_uri=http%3A%2F%2Fflask.huchangyi.com%2Fuserinfo&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect"
        },
        {
            "name": "菜单一",
            "sub_button": [
                {
                    "type": "click",
                    "name": "点击",
                    "key": "click"
                },
                {
                    "type": "view",
                    "name": "网站",
                    "url": "http://www.huchangyi.com/",
                    "key": "view"
                },
                {
                    "type": "scancode_push",
                    "name": "扫码",
                    "key": "scancode_push"
                },
                {
                    "type": "scancode_waitmsg",
                    "name": "扫码确认",
                    "key": "scancode_waitmsg"
                },
                {
                    "type": "pic_sysphoto",
                    "name": "拍照",
                    "key": "pic_sysphoto"
                }
            ]
        },
        {
            "name": "菜单二",
            "sub_button": [
                {
                    "type": "pic_photo_or_album",
                    "name": "拍照选择",
                    "key": "pic_photo_or_album"
                },
                {
                    "type": "pic_weixin",
                    "name": "相册",
                    "key": "pic_weixin"
                },
                {
                    "type": "location_select",
                    "name": "地理位置",
                    "key": "location_select"
                }
            ]
        }
    ]
    }
    postData = json.dumps(postData, ensure_ascii=False).encode('utf-8')
    resString = requests.post(postUrl, data=postData).text
    return resString


@app.route('/get_menu/', methods=['GET', 'POST'])
def get_menu():
    access_token = get_access_token()
    getUrl = "https://api.weixin.qq.com/cgi-bin/menu/get?access_token=" + access_token
    resString = requests.get(getUrl).text
    return resString


@app.route('/delete_menu/', methods=['GET', 'POST'])
def delete_menu():
    access_token = get_access_token()
    getUrl = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=" + access_token
    resString = requests.get(getUrl).text
    return resString


@app.route('/wifi/', methods=['GET', 'POST'])
def wifi():
    return render_template('wifi.html')


@app.route('/openplugin/', methods=['GET', 'POST'])
def openplugin():
    access_token = get_access_token()
    getUrl = "https://api.weixin.qq.com/bizwifi/openplugin/token?access_token=" + access_token
    postData = {
        "callback_url": "http://flask.huchangyi.com/"
    }
    postData = json.dumps(postData, ensure_ascii=False).encode('utf-8')
    resString = requests.post(getUrl, data=postData).text
    return resString


@app.route('/web/', methods=['GET', 'POST'])
def web():
    """
    以snsapi_base为scope发起的网页授权，是用来获取进入页面的用户的openid的，并且是静默授权并自动跳转到回调页的。用户感知的就是直接进入了回调页（往往是业务页面）
    以snsapi_userinfo为scope发起的网页授权，是用来获取用户的基本信息的。但这种授权需要用户手动同意，并且由于用户同意过，所以无须关注，就可在授权后获取该用户的基本信息。
    定义返回地址后，已微信要求的格式传参
    """
    myUrl = "http://flask.huchangyi.com/userinfo"
    myUrl = urllib.parse.quote(myUrl, safe='')
    urlString = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
                + appid \
                + "&redirect_uri=" + myUrl \
                + "&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect"
    return redirect(urlString)


@app.route('/userinfo/', methods=['GET', 'POST'])
def userinfo():
    """
    userinfo的前段展示页,调用web后会由微信重定向到此页并附带参数
    :return:
    """
    data = request.args
    if(data != None):
        code = data.get("code")
        state = data.get("state")
        #根据跳转后的code，获取网页的access_token
        token_data = get_web_access_token(code)
        web_access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        openid = token_data.get("openid")
        #根据网页的access_token等，获取用户基础信息
        userinfo_data = get_web_userinfo(web_access_token, openid)
        nickname = userinfo_data.get("nickname")
        sex = userinfo_data.get("sex")
        province = userinfo_data.get("province")
        city = userinfo_data.get("city")
        country = userinfo_data.get("country")
        headimgurl = userinfo_data.get("headimgurl").replace("\/", "/")
    return render_template('userinfo.html', code=code, state=state,
                           web_access_token=web_access_token, refresh_token=refresh_token, openid=openid,
                           nickname=nickname, sex=sex, province=province, city=city, country=country, headimgurl=headimgurl)


@app.route('/get_web_access_token/', methods=['GET', 'POST'])
def get_web_access_token(code):
    """
    根据跳转后的code，获取网页的access_token
    :param code:
    :return:
    """
    url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=" \
          + appid + "&secret=" \
          + appsecret + "&code=" \
          + code + "&grant_type=authorization_code"
    data = requests.get(url).text
    data = eval(data)
    return data


@app.route('/get_web_userinfo/', methods=['GET', 'POST'])
def get_web_userinfo(web_access_token, openid):
    """
    根据网页的access_token等，获取用户基础信息
    :param web_access_token:
    :param openid:
    :return:返回
    """
    url = "https://api.weixin.qq.com/sns/userinfo?access_token=" + web_access_token + "&openid=" + openid + "&lang=zh_CN"
    data = requests.get(url)
    data = data.text.encode(data.encoding).decode('utf-8')
    data = eval(data)
    return data


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='flask.log',
                        filemode='w')
    app.run(
        app.run(host="0.0.0.0", port=80)
    )

