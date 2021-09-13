from settings import UA, LOGIN_REFERER,LOGIN_API,LIST_CONTENTS,LIST_TAGS,MAX_ERROR_COUNT
import requests
import json
import os
import random

def generate_cookies(app=None):
    USERNAME = os.getenv("FLOMO_USERNAME","")
    PASSWORD = os.getenv("FLOMO_PASSWORD","")
    LOGIN_HEADERS= {
        "user-agent": UA,
        "referer": LOGIN_REFERER
    }
    data = {
        "email":USERNAME,
        "password":PASSWORD
    }
    req = requests.post(LOGIN_API, data=data, headers=LOGIN_HEADERS, verify=False)
    if req.status_code == 200 and req.json()["code"] == 0:
        cookies = req.cookies.get_dict()
        with open("./cookies.json","w") as file:
            json.dump(cookies, file)
        return cookies
    else:
        app.logger.error(f"Login Flomo Error：{req.json()}")

def load_cookies():
    with open("./cookies.json","r") as file:
        cookies = json.load(file)
        return cookies

def pull_tags(app=None, cookies=None):
    try:
        body = requests.get(LIST_TAGS,headers={"user-agent": UA}, cookies=cookies)
        jsContent = body.json()
        if body.status_code == 200 and body["code"] == 0 and "tag_names" in jsContent:
            return jsContent["tag_names"]
    except Exception as e:
        app.logger.error(f"Pull tags error: {e.args}")
    return []

def pull_contents(app=None, cookies=None):
    try:
        parmas = {
            "tag": "",
            "tz": "8:0"
        }
        body = requests.get(LIST_CONTENTS, params=parmas, headers={"user-agent": UA}, cookies=cookies, verify=False)
        jsContent = body.json()
        if body.status_code == 200 and jsContent["code"] == 0 and "memos" in jsContent:
            return jsContent["memos"]
    except Exception as e:
        app.logger.error(f"Error：{e.args}")
    return []

def get_article(app=None):
    cookies = load_cookies()
    if not cookies:
        cookies = generate_cookies(app)
    error_counts = 0
    while error_counts < MAX_ERROR_COUNT :
        contents = pull_contents(app, cookies)
        if len(contents) > 0:
            return random.choice(contents)
        app.logger.warning(f"Error pull contents:{error_counts}")
        error_counts += 1
        cookies = generate_cookies(app)

def assert_flomo_ad(article):
    return "flomo" in article   