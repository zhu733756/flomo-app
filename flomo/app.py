# -*- coding: UTF-8 -*-

from flask import Flask, request, make_response
import os
from wechat_sdk import WechatConf
from wechat_sdk import WechatBasic
from werkzeug import datastructures
from app_flomo import get_article
import re
import time

app = Flask(__name__)

AES_KEY = os.getenv("AES_KEY","")
wechatConf = WechatConf(
    token=os.getenv("TOKEN",""),
    appid=os.getenv("APPID",""),
    appsecret=os.getenv("APPSECRET",""),
    encrypt_mode="compatible"
)
wechatConf.encoding_aes_key = AES_KEY if AES_KEY else None
wechat = WechatBasic(conf=wechatConf)

registers = set()

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
        wechat.parse_data(request.data)
        wechat_message = wechat.message
        response = wechat.response_none()      
        if wechat_message.type == 'text':
            content = wechat_message.content
            if content == "#注册":
                registers.add(wechat_message.source)
                response = wechat.response_text("注册成功")
            elif content == "#取消注册":
                registers.remove(wechat_message.source)
                response = wechat.response_text("取消注册成功")
            elif content in ("笔记"):
                artile = pure_article(get_article(app)["content"])
                response = wechat.response_text(artile)
            elif content in ("flomo"):
                slug = get_article(app)["slug"]
                response = wechat.response_text(f"https://flomoapp.com/mine?memo_id={slug}")
            elif content in ("prometheus","prom"):
                response = wechat.response_text("链接：https://pan.baidu.com/s/1ej8sCmbt1mOD8rM4jV9q3A 提取码：prom") 
            elif content in ("科学上网"):
                response = wechat.response_text("链接：https://pan.baidu.com/s/1_3qDjmdSd7hZM71aEQfb4g 提取码：ti8j")

        response = make_response(response)
        response.content_type = 'application/xml'
        return response

@app.route("/flomo/cronjobs", methods=["GET"])
def reply_registriers():
    for source in registers:
        artile_content = pure_article(get_article(app)["content"])
        app.logger.info(f"Send to user {source}, Article: {artile_content}")
        post_singlesend(source, artile_content)
        time.sleep(0.5)
    response = make_response(f"registers: {','.join(registers)} 发送成功")
    return response

def post_singlesend(source, article_content):
    url = "https://mp.weixin.qq.com/cgi-bin/singlesend"
    data = {
        "token": wechat.grant_token(),
        "lang": "zh_CN",
        "f": "json",
        "ajax": "1",
        "mask": "false",
        "tofakeid": source,
        "type": 1,
        "content": article_content,
        "appmsg":"", 
    }
    wechat.request.post(url, data=data)
        
def pure_article(artcile):
    pat1 = re.compile(r'<[^>]+>',re.S)
    pat2 = re.compile(r'<[^/]+>',re.S)
    return pat1.sub('\n', pat2.sub('', artcile))


if __name__ == '__main__':
    app.run("0.0.0.0", 5000, debug=False)
