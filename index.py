# -*- coding: utf-8 -*-
import requests

PUSHDEER_KEY = "PDU42336TT60JkqHMGFLcKdETkZcjRTg83nNIMBaT"

def test_push():
    url = "https://api2.pushdeer.com/message/push"
    data = {
        "pushkey": PUSHDEER_KEY,
        "text": "🚨 自动化定时器极限测试",
        "desp": "如果你收到这条消息，说明 GitHub 的 5 分钟闹钟完全活过来了！"
    }
    res = requests.post(url, data=data, timeout=10)
    print("推送响应结果:", res.text)

if __name__ == "__main__":
    test_push()
