# -*- coding: utf-8 -*-
import requests

# ==========================================
# 🔧 个人配置区
# ==========================================
PUSHDEER_KEY = "PDU42336TT60JkqHMGFLcKdETkZcjRTg83nNIMBaT"  # 📌 你的 PushDeer Key
# ==========================================

def main_handler():
    print("🚀 GitHub Actions 测试发射架已启动...")
    
    title = "🎉 祝贺！你的 GitHubActions 搬家大获成功！"
    content = "### ☁️ 来自 GitHub Actions 云端的问候\n\n如果你能看到这条微信，说明：\n1. 你的 GitHub 仓库配置**100% 正确**。\n2. 定时闹钟已经充能完毕。\n3. 我们已经彻底摆脱了腾讯云的收费枷锁，开启白嫖时代！"
    
    url = "https://api2.pushdeer.com/message/push"
    data = {
        "pushkey": PUSHDEER_KEY,
        "text": title,
        "desp": content,
        "type": "markdown"
    }
    
    try:
        res = requests.post(url, data=data, timeout=15).json()
        print(f"📡 微信推送渠道反馈: {res}")
        print("✨ 测试简报已成功发射！请检查手机微信。")
    except Exception as e:
        print(f"❌ 发送失败，原因: {e}")

if __name__ == "__main__":
    main_handler()
