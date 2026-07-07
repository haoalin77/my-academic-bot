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
    # 🧪 1. 试剂配置逻辑（锚定 2026年7月10日，9天一循环）
    # ----------------------------------------------------
    reagent_anchor = datetime(2026, 7, 7).date()
    delta_reagent = (today - reagent_anchor).days
    reagent_mod = delta_reagent % 5

    if reagent_mod == 0:
        reagent_msg = "🔴 **【今日任务】今天必须配置新试剂！**"
    else:
        days_left_reagent = 5 - reagent_mod
        next_reagent_date = today + timedelta(days=days_left_reagent)
        reagent_msg = f"⏳【试剂进度】今天无需配置。距离下次配置还有 **{days_left_reagent}** 天（预计 `{next_reagent_date.strftime('%m-%d')}`）。"

    # ----------------------------------------------------
    # 🧫 2. 培养基配置逻辑（锚定 2026年7月6日，6天一循环）
    # ----------------------------------------------------
    medium_anchor = datetime(2026, 7, 6).date()
    delta_medium = (today - medium_anchor).days
    medium_mod = delta_medium % 6

    if medium_mod == 0:
        medium_msg = "🔴 **【今日任务】今天必须配置新培养基！**"
    else:
        days_left_medium = 6 - medium_mod
        next_medium_date = today + timedelta(days=days_left_medium)
        medium_msg = f"⏳【培养基进度】今天无需配置。距离下次配置还有 **{days_left_medium}** 天（预计 `{next_medium_date.strftime('%m-%d')}`）。"

    # ----------------------------------------------------
    # 📋 3. 组装最终发送的 Markdown 文本
    # ----------------------------------------------------
    push_title = f"🧪 实验排班提醒 ({today.strftime('%m-%d')})"

    markdown_content = f"### 📅 实验试剂/培养基排班雷达\n\n"
    markdown_content += f"- {reagent_msg}\n"
    markdown_content += f"- {medium_msg}\n\n"
    markdown_content += f"---\n"
    markdown_content += f"💡 *💡 记得在实验记录本上同步登记日志哦！*"

    print("正在打印生成的提醒内容：")
    print(markdown_content)

    # 执行发送
    send_pushdeer_msg(push_title, markdown_content)

if __name__ == "__main__":
    calculate_reminders()