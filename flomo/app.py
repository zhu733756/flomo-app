from flask import Flask, request,  make_response
import os
from wechat_sdk import WechatConf
from wechat_sdk import WechatBasic
from app_flomo import get_article
import xml.etree.ElementTree as ET
import time
import re

app = Flask(__name__)

wechatConf = WechatConf(
    token=os.getenv("TOKEN",""),
    appid=os.getenv("APPID",""),
    appsecret=os.getenv("APPSECRET","")
    # encrypt_mode="safe",
)

wechat = WechatBasic(conf=wechatConf)

@app.route("/flomo", methods=["GET","POST"])
def flomo_article():
    echostr = request.values.get('echostr', '')
    signature = request.values.get('signature', '')
    timestamp = request.values.get('timestamp', '')
    nonce = request.values.get('nonce', '')
    app.logger.debug('signature=%s, timestamp=%s, nonce=%s, echostr=%s', signature, timestamp, nonce, echostr)
    if wechat.check_signature(signature, timestamp, nonce):
        app.logger.info("wechat check_signature OK")
    else:
        app.logger.warning("Signature check failed.")
        return make_response("Signature check failed.")
    if request.method == "GET":
        return make_response(echostr)
    else:
        xml = ET.fromstring(request.data)
        toUser = xml.find('ToUserName').text
        fromUser = xml.find('FromUserName').text
        msgType = xml.find("MsgType").text

        if msgType == 'text':
            content = xml.find('Content').text
            if content in ("笔记"):
                artile = get_article(app)
                return reply_text(fromUser,toUser, pure_article(artile["content"]))

            if content in ("flomo"):
                artile = get_article(app)
                slug = artile["slug"]
                return reply_text(fromUser,toUser, f"https://flomoapp.com/mine?memo_id={slug}")

            if content in ("prometheus","prom"):
                return reply_text(fromUser,toUser, "链接：https://pan.baidu.com/s/1ej8sCmbt1mOD8rM4jV9q3A 提取码：prom")
            
            if content in ("科学上网"):
                return reply_text(fromUser,toUser, "链接：https://pan.baidu.com/s/1_3qDjmdSd7hZM71aEQfb4g 提取码：ti8j")

        
        return reply_text(fromUser,toUser, "你再说一遍？我听不懂")

def pure_article(artcile):
    pat = re.compile(r'<[^>]+>',re.S)
    return pat.sub('', artcile)

def reply_text(to_user, from_user, content):
    reply = """
    <xml><ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    <FuncFlag>0</FuncFlag></xml>
    """
    response = make_response(reply % (to_user, from_user,
                                      str(int(time.time())), content))
    response.content_type = 'application/xml'
    return response


if __name__ == '__main__':
    app.run("0.0.0.0", 5000, debug=False)
    