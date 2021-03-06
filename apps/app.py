# -*- coding: UTF-8 -*-

from random import random
from flask import Flask, request, make_response, render_template_string
import os
# from wechat_sdk import WechatConf
# from wechat_sdk import WechatBasic
from app_flomo import get_article
import re
import time
import subprocess
# import random

app = Flask(__name__)

# AES_KEY = os.getenv("AES_KEY","")
# wechatConf = WechatConf(
#     token=os.getenv("TOKEN",""),
#     appid=os.getenv("APPID",""),
#     appsecret=os.getenv("APPSECRET",""),
#     encrypt_mode="compatible"
# )
# wechatConf.encoding_aes_key = AES_KEY if AES_KEY else None
# wechat = WechatBasic(conf=wechatConf)

# registers = set()

template = """
{% for line in lines %}
<pre>
    {{ line }}
</pre>
{% endfor %}
"""

flomo_articles_count = 0
algorithm_articles_count = 0
max_number = 2**8-1


# @app.route("/app/flomo", methods=["GET","POST"])
# def flomo_article():
#     echostr = request.values.get('echostr', '')
#     signature = request.values.get('signature', '')
#     timestamp = request.values.get('timestamp', '')
#     nonce = request.values.get('nonce', '')
#     app.logger.debug('signature=%s, timestamp=%s, nonce=%s, echostr=%s', signature, timestamp, nonce, echostr)
#     if wechat.check_signature(signature, timestamp, nonce):
#         app.logger.info("wechat check_signature OK")
#     else:
#         app.logger.warning("Signature check failed.")
#         return make_response("Signature check failed.")
#     if request.method == "GET":
#         return make_response(echostr)
#     else:
#         wechat.parse_data(request.data)
#         wechat_message = wechat.message
#         response = wechat.response_none()      
#         if wechat_message.type == 'text':
#             article = random.choice(get_article(app))
#             content = wechat_message.content
#             if content == "#注册":
#                 registers.add(wechat_message.source)
#                 response = wechat.response_text("注册成功")
#             elif content == "#取消注册":
#                 registers.remove(wechat_message.source)
#                 response = wechat.response_text("取消注册成功")
#             elif content in ("笔记"):
#                 artile = pure_article(article["content"])
#                 response = wechat.response_text(artile)
#             elif content in ("flomo"):
#                 slug = article["slug"]
#                 response = wechat.response_text(f"https://flomoapp.com/mine?memo_id={slug}")
#             elif content in ("prometheus","prom"):
#                 response = wechat.response_text("链接：https://pan.baidu.com/s/1ej8sCmbt1mOD8rM4jV9q3A 提取码：prom") 
#             elif content in ("科学上网"):
#                 response = wechat.response_text("链接：https://pan.baidu.com/s/1_3qDjmdSd7hZM71aEQfb4g 提取码：ti8j")

#         response = make_response(response)
#         response.content_type = 'application/xml'
#         return response

@app.route("/app/flomo/articles/random", methods=["GET"])
def get_flomo_articles():
    global flomo_articles_count
    global max_number
    content = request.values.get('dashuaibi', '')
    articles = get_article(app)
    flomo_articles_count = flomo_articles_count&max_number + 1
    article = articles[flomo_articles_count % (len(articles)-1)]
    if content == "zhu733756":
        artile = article["content"]
    else:
        slug = article['slug']
        artile = f"https://flomoapp.com/mine?memo_id={slug}"
    return make_response(artile)

@app.route("/app/algorithmCoding/repo/update", methods=["GET"])
def update_github_repo():
    content = request.values.get('dashuaibi', '')
    r_token = request.values.get('token', '')
    token = os.getenv("TOKEN","")
    response = "ok"
    if content == "zhu733756" and r_token == token:
        completed = subprocess.run(['cd','/gitRepo/AlgorithmCoding','&&','git', 'pull', 'origin', 'master'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed.stdout or completed.stderr:
            response = completed.stdout or completed.stderr
    return  make_response(response)

@app.route("/app/algorithmCoding/articles/random", methods=["GET"])
def get_algorithm_coding_articles():
    global algorithm_articles_count
    global max_number
    content = request.values.get('dashuaibi', '')
    lines = []
    if content == "zhu733756":
        paths = []
        recursive("/gitRepo/AlgorithmCoding/", paths=paths)
        if paths:
            algorithm_articles_count = (algorithm_articles_count & max_number) + 1
            article_path = paths[algorithm_articles_count % (len(paths)-1)]
            try:
                with open(article_path, "r", encoding="utf-8") as file:
                    for line in file.readlines():
                        lines.append(line.rstrip("\n"))
            except Exception as e:
                app.logger.error(f"Error: {e.args}")
    return render_template_string(template, lines=lines)

# @app.route("/app/flomo/cronjobs", methods=["GET"])
# def reply_registers():
#     for source in registers:
#         artile_content = pure_article(get_article(app)["content"])
#         app.logger.info(f"Send to user {source}, Article: {artile_content}")
#         post_singlesend(source, artile_content)
#         time.sleep(0.5)
#     response = make_response(f"registers: {','.join(registers)} 发送成功")
#     return response

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

def recursive(dirpath, suffix="py", paths = []):
    for path in os.listdir(dirpath):
        curpath = os.path.join(dirpath, path)
        if os.path.isdir(curpath):
            recursive(curpath, suffix, paths)
        elif path.endswith(suffix) and not path.startswith("__init__"):
            paths.append(curpath)




if __name__ == '__main__':
    app.run("0.0.0.0", 5000, debug=False)
