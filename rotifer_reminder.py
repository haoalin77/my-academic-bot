# -*- coding: utf-8 -*-
import os
import requests
import urllib3
from datetime import datetime, timedelta
import time
import sys

# 禁用安全警告（保持和你原有脚本一致的严谨性）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 🔧 通用配置区
# ==========================================
SEND_KEY = "SCT316351T9sZW7a3Jjsa1cTc1Jwb9I1Ma"
# ==========================================

def send_wechat_msg(push_title, markdown_content):
    """通过 Server酱 发送微信通知"""
    if SEND_KEY == "YOUR_SEND_KEY" or not SEND_KEY:
        print("    ⚠️ 未配置 SendKey，跳过微信推送。")
        return

    push_url = f"https://sctapi.ftqq.com/{SEND_KEY}.send"
    data = {
        "title": push_title,
        "desp": markdown_content
    }
    try:
        response = requests.post(push_url, data=data)
        if response.status_code == 200:
            print("    📲 微信推送成功！请查看手机。")
        else:
            print(f"    ❌ 微信推送失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"    ❌ 微信推送报错: {e}")

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
    send_wechat_msg(push_title, markdown_content)

if __name__ == "__main__":
    print("⏸️ 提醒服务已暂停")
    # 直接 exit() 或 return，阻断后续的程序执行
    #import sys
    #sys.exit(0)
    calculate_reminders()