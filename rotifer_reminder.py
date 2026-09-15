# -*- coding: utf-8 -*-
import os
import requests
import urllib3
from datetime import datetime, timedelta

# 禁用安全警告（保持和你原有脚本一致的严谨性）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 🔧 通用配置区
# ==========================================
PUSHDEER_KEY = "PDU42336TT60JkqHMGFLcKdETkZcjRTg83nNIMBaT"  # 📌 你的 PushDeer Key
# ==========================================

def send_pushdeer_msg(title, content):
    """通过 PushDeer 发送微信 Markdown 推送"""
    url = "https://api2.pushdeer.com/message/push"
    data = {
        "pushkey": PUSHDEER_KEY,
        "text": title,
        "desp": content,
        "type": "markdown"
    }
    try:
        res = requests.post(url, data=data, timeout=15)
        result = res.json()
        res_str = str(result.get("content", {}).get("result", ""))
        if result.get("code") == 0 or "ok" in res_str.lower():
            print(f"📡 PushDeer 实验渠道推送成功: {title}")
            return True
        else:
            print(f"❌ PushDeer 实验推送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 微信推送发生异常: {e}")
        return False

def calculate_reminders():
    # 获取今天的北京时间
    today = datetime.now().date()

    # ----------------------------------------------------
    # 🧫 3. 培养基EPA
    # ----------------------------------------------------
    keep_msg = "**【今日任务】今天记得轮虫保种！**"


    # ----------------------------------------------------
    # 📋 4. 组装最终发送的 Markdown 文本
    # ----------------------------------------------------
    push_title = f"🧪 今日轮虫保种 ({today.strftime('%m-%d')})"

    markdown_content = f"### 📅 轮虫保种提醒\n\n"
    markdown_content += f"- {keep_msg}\n\n"
    markdown_content += f"---\n"
    markdown_content += f"💡 *💡 记得今天轮虫保种！*"

    print("正在打印生成的提醒内容：")
    print(markdown_content)

    # 执行发送
    send_pushdeer_msg(push_title, markdown_content)

if __name__ == "__main__":
    print("⏸️ 提醒服务已暂停")
    # 直接 exit() 或 return，阻断后续的程序执行
    #import sys
    #sys.exit(0)
    calculate_reminders()