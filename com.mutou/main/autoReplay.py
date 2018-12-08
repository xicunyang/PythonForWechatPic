import itchat
import requests
import json
import os
import random
from io import BytesIO
from PIL import Image

# 图灵的URL
TU_LING_URL = "http://openapi.tuling123.com/openapi/api/v2"

# 移动文件路径
TO_PATH = "/Users/mutou/Desktop/test/"


def login():
    # 是否自动登录
    itchat.auto_login(hotReload=True)
    # itchat.login()


def get_tuling_word(user_name, user_word):
    # 组装请求参数
    # 因为userId不能接收太长的值  所以截取1-10
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": user_word
            }
        },
        "userInfo": {
            "apiKey": "270bfecc32ef452ab6596354a21f41fb",
            "userId": user_name[1:10]
        }
    }

    # 请求  post
    response = requests.post(TU_LING_URL, json=data).text

    # 解析返回数据
    json_obj = json.loads(response)

    # print(json_obj)

    result_type = json_obj["results"][0]["resultType"]

    print(result_type)

    if result_type == "text":
        # 获取到返回的值
        response_word = json_obj["results"][0]["values"]["text"]
        # 返回回去
        return response_word
    elif result_type == "image":
        image_url = json_obj["results"][0]["values"]["image"]
        response_pic = requests.get(image_url)
        # 保存图片
        image = Image.open(BytesIO(response_pic.content))
        image.save('cache_tu_ling.jpg')
        return "yxc945xxx"



def get_tuling_pic():
    authers = ["金馆长", "柴犬", "赵雷", "黄渤", "暴漫", "岳云鹏", "猴子"]
    auther_random = authers[random.randint(0, len(authers) - 1)]
    # 组装请求参数
    url = "https://www.doutula.com/api/search?keyword=" + auther_random + "&mime=0&page=1"
    # 请求  post
    response = requests.post(url).text
    # print(response)
    # 解析返回数据
    json_obj = json.loads(response)
    # 获得list
    image_urls = json_obj["data"]["list"]
    # 获取到获取的图片的数量
    images_count = len(image_urls)
    # 生成一个随机数
    image_random_count = random.randint(0, images_count - 1)
    image_ramdom = image_urls[image_random_count]

    # 得到最后的图片地址
    final_image_url = image_ramdom["image_url"]
    # print(final_image_url)
    # 请求图片地址
    response_pic = requests.get(final_image_url)
    # 保存图片
    image = Image.open(BytesIO(response_pic.content))
    image.save('cache.gif')

    # 获取到的动态图有问题  不能动
    # urllib.request.urlretrieve("http://ws1.sinaimg.cn/bmiddle/6af89bc8gw1f8pmzx3ewfg202i02iq4u.gif", 'test2.gif')


# @itchat.msg_register('Text')
def text_replay(msg):
    global is_continue
    # 当消息不是自己发出的时候
    # 获取到该用户的用户名称
    from_user_name = msg['FromUserName']
    user_word = msg['Text']
    user_name = msg["User"]["UserName"]

    print(is_continue)
    print(from_user_name)
    print(user_word)

    if not from_user_name == myUserName:
        # 只有当全局变量为True
        if is_continue == True:
            return get_tuling_word(from_user_name, user_word)

    elif user_name == "filehelper":
        if user_word == "stop":
            is_continue = False
        elif user_word == "continue":
            is_continue = True


@itchat.msg_register(['Text', 'Picture', 'Recording'])
def all_replay(recv_msg):
    """
    包括  ：  文字 + 图片 + 语音
    :param recv_msg:  入参
    :return:
    """
    # 根据MsgType进行判断
    # 34  语音
    # 47  表情包
    # 3 图片
    # 1 文字

    global is_continue
    # 当消息不是自己发出的时候
    # 获取到该用户的用户名称
    from_user_name = recv_msg['FromUserName']
    user_word = recv_msg['Text']
    user_name = recv_msg["User"]["UserName"]

    # print(recv_msg)

    # 根据消息类型进行判断是否是文字消息
    if recv_msg["MsgType"] == 1:
        # 文字消息
        if not from_user_name == myUserName:
            # 只有当全局变量为True
            if is_continue == True:
                return_word = get_tuling_word(from_user_name, user_word)
                if return_word == "yxc945xxx":
                    # 返回图片
                    # 因为图灵有时候会返回图片
                    itchat.send_image('cache_tu_ling.jpg', toUserName=from_user_name)
                else:
                    return return_word

        elif user_name == "filehelper":
            # 发送给文件助手  停止/开始
            if user_word == "1":
                is_continue = True
                itchat.send("开始...")

            elif user_word == "2":
                is_continue = False
                itchat.send("暂停...")

    else:
        if is_continue == True:
            # 非文字消息
            # 下载文件  各种文件
            recv_msg['Text'](recv_msg['FileName'])
            # 将文件移动到指定目录
            # change_place(recv_msg['FileName'], TO_PATH + recv_msg['FileName'])
            # 处理文件
            # 判断文件类型
            if recv_msg["MsgType"] == 3 or recv_msg["MsgType"] == 47:
                # 图片 或者 表情包
                # 得到图片的接口
                # open_url = "XXX" + recv_msg
                # open_url = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1544269191538&di=10d16f4e3af8df7ad96a011fe1a1d331&imgtype=0&src=http%3A%2F%2Fimg.bqatj.com%2Fimg%2Fe0a7e141b984c4d6.jpg"
                get_tuling_pic()
                itchat.send_image('cache.gif', toUserName=from_user_name)
            # 清理文件
            os.remove(recv_msg['FileName'])


def change_place(from_path, to_path):
    # 为的是将当前目录下的图片文件转移到tomcat服务器下 供外网调用
    # from_path = "/Users/mutou/Desktop/pager.png"
    f_from = open(from_path, "rb")
    from_file = f_from.read()
    f_from.close()

    # to_path = "/Users/mutou/Desktop/test/test1.png"
    f_to = open(to_path, "wb")
    f_to.write(from_file)
    f_to.close()

    # 删除原来的
    os.remove(from_path)


if __name__ == '__main__':
    is_continue = True
    # 登录
    login()

    # 获取自己的UserName
    myUserName = itchat.get_friends(update=True)[0]["UserName"]
    itchat.run()
