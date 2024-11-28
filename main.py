import base64
import json
import os
from datetime import datetime

import requests


def bark(device_key, title, content, bark_icon):
    if not device_key:
        return 2

    url = "https://api.day.app/push"
    headers = {
        "content-type": "application/json",
        "charset": "utf-8"
    }
    data = {
        "title": title,
        "body": content,
        "device_key": device_key
    }

    if not bark_icon:
        bark_icon = ''
    if len(bark_icon) > 0:
        url += '?icon=' + bark_icon
        print('拼接icon')
    else:
        print('不拼接icon')

    resp = requests.post(url, headers=headers, data=json.dumps(data))
    resp_json = resp.json()
    if resp_json["code"] == 200:
        print(f"[Bark]Send message to Bark successfully.")
    if resp_json["code"] != 200:
        print(f"[Bark][Send Message Response]{resp.text}")
        return -1
    return 0


def gitee_sha(access_token, owner, repo, path):
    url = "https://gitee.com/api/v5/repos/" + owner + "/" + repo + "/contents/" + path + "?access_token=" + access_token
    headers = {
        "content-type": "application/json",
        "charset": "utf-8"
    }

    resp = requests.get(url, headers=headers)
    resp_json = resp.json()
    return resp_json["sha"]


def gitee_commit(access_token, owner, repo, path, content, sha, message):
    url = "https://gitee.com/api/v5/repos/" + owner + "/" + repo + "/contents/" + path
    headers = {
        "content-type": "application/json",
        "charset": "utf-8"
    }
    data = {
        "access_token": access_token,
        "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        "sha": sha,
        "message": message
    }

    resp = requests.put(url, headers=headers, data=json.dumps(data))
    resp_json = resp.json()
    return resp_json


def main():
    bark_device_key = os.environ.get('BARK_DEVICEKEY')
    bark_icon = os.environ.get('BARK_ICON')

    access_token = os.environ.get('GITEE_ACCESS_TOKEN')
    owner = os.environ.get('GITEE_OWNER')
    repo = os.environ.get('GITEE_REPO')
    path = os.environ.get('GITEE_PATH')

    current_time = datetime.now()
    content = current_time.strftime('%Y-%m-%d %H:%M:%S')
    git_sha = ''
    git_message = '1'

    title = 'gitee-签到结果'
    message = 'pull操作成功'
    commit_success = False

    try:
        git_sha = gitee_sha(access_token, owner, repo, path)
    except Exception as e:
        git_sha = ''
        message = 'sha操作失败 ->' + str(e)
        print('git_sha Error')

    if git_sha:
        res = gitee_commit(access_token, owner, repo, path, content, git_sha, git_message)
        if res:
            try:
                message = 'pull操作成功 返回值解析成功 ->' + res['content']['name']
                commit_success = True
            except Exception as e:
                message = 'pull操作成功 返回值解析失败 ->' + str(e)
                print('git_pull Error')
        else:
            message = 'pull操作失败'
    else:
        message = 'sha为空'
        print('git_sha Empty')

    if commit_success:
        current_hour = datetime.now().hour
        if 8 <= current_hour <= 12:
            print('current_hour need send')
            bark(bark_device_key, title, message, bark_icon)
        else:
            print('current_hour not need send')
    else:
        bark(bark_device_key, title, message, bark_icon)

    print('finish')


if __name__ == '__main__':
    main()
