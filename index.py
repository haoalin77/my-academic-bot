# -*- coding: utf-8 -*-
import imaplib
import email
import re
import time
import os
import requests
import xml.etree.ElementTree as ET
import urllib3
from bs4 import BeautifulSoup
from email.header import decode_header
from urllib.parse import quote
from datetime import datetime, timedelta

# 禁用安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

imaplib.Commands['ID'] = ('AUTH')

# ==========================================
# 🔧 腾讯云网页端通用配置区
# ==========================================
EMAIL_USER = "needliulin@163.com"        # 网易邮箱账号
EMAIL_PASS = "XHgxdaafJTTXv2sk"          # 网易邮箱授权码
PUSHDEER_KEY = "PDU42336TT60JkqHMGFLcKdETkZcjRTg83nNIMBaT"  # 📌 你的 PushDeer Key
DAYS_LIMIT = 10                          # 高校新闻爬取近 10 天的数据
# ==========================================

def translate_safe_chunk(text):
    """底层翻译函数"""
    if not text.strip(): return ""
    try:
        url = f"https://api.mymemory.translated.net/get?q={quote(text)}&langpair=en|zh-CN&de={EMAIL_USER}"
        resp = requests.get(url, timeout=10).json()
        translated = resp.get('responseData', {}).get('translatedText', '')

        if "MYMEMORY WARNING" in translated.upper() or "YOU USED ALL AVAILABLE" in translated.upper():
            print("⚠️ [警告] MyMemory 接口今日额度已耗尽，启动英文原文兜底。")
            return "[额度超限，请看英文原文]"
        return translated
    except Exception as e:
        print(f"❌ 翻译请求异常: {e}")
        return "[片段翻译失败]"

def smart_translate(text, original_fallback=""):
    """智能切片翻译逻辑"""
    if not text: return "无摘要内容"
    sentences = text.split('. ')
    translated_results = []
    current_batch = ""

    for s in sentences:
        if len(current_batch) + len(s) < 350:
            current_batch += s + ". "
        else:
            res = translate_safe_chunk(current_batch)
            if "[额度超限" in res:
                return original_fallback if original_fallback else text
            translated_results.append(res)
            current_batch = s + ". "
            time.sleep(1.5)

    if current_batch:
        res = translate_safe_chunk(current_batch)
        if "[额度超限" in res:
            return original_fallback if original_fallback else text
        translated_results.append(res)

    final_zh = "".join(translated_results)
    if not final_zh.strip() or final_zh == "[片段翻译失败]":
        return original_fallback if original_fallback else text
    return final_zh

def get_paper_from_pubmed(doi):
    """引擎 A: PubMed 官方接口"""
    try:
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={doi}[LocationID]&retmode=json"
        search_res = requests.get(search_url, timeout=10).json()
        ids = search_res.get('esearchresult', {}).get('idlist', [])
        if not ids: return None, None

        fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids[0]}&retmode=xml"
        fetch_res = requests.get(fetch_url, timeout=10)
        root = ET.fromstring(fetch_res.text)

        title = root.find('.//ArticleTitle').text if root.find('.//ArticleTitle') is not None else "Untitled"
        abs_elements = root.findall('.//AbstractText')
        abstract = " ".join([el.text for el in abs_elements if el.text])
        return title, abstract
    except:
        return None, None

def get_paper_from_ss(doi):
    """引擎 B: Semantic Scholar 兜底"""
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,abstract"
        res = requests.get(url, timeout=10).json()
        return res.get('title'), res.get('abstract')
    except:
        return None, None

def send_pushdeer_msg(title, content):
    """通过 PushDeer 发送微信 Markdown 推送 (兼容新老格式判定)"""
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
            print(f"📡 PushDeer 渠道推送成功: {title}")
            return True
        else:
            print(f"❌ PushDeer 推送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 微信推送发生异常: {e}")
        return False

def get_ahnu_news_report():
    """执行安师大核心爬取逻辑"""
    today = datetime.now()
    start_date = today - timedelta(days=DAYS_LIMIT)

    tasks = [
        ["生环学院-通知公告", "https://envirsci.ahnu.edu.cn/tzgg.htm", "https://envirsci.ahnu.edu.cn/"],
        ["生环学院-学院新闻", "https://envirsci.ahnu.edu.cn/xyxw.htm", "https://envirsci.ahnu.edu.cn/"],
        ["研究生院-通知公告", "https://gs.ahnu.edu.cn/tzgg.htm", "https://gs.ahnu.edu.cn/"],
        ["研究生院-新闻动态", "https://gs.ahnu.edu.cn/xwdt.htm", "https://gs.ahnu.edu.cn/"]
    ]

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0"}
    full_report = f"### 📅 监控范围：{start_date.strftime('%Y-%m-%d')} 至今\n\n"
    found_any = False

    for name, url, base_url in tasks:
        try:
            res = requests.get(url, headers=headers, verify=False, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all('li')

            section_text = f"#### 🔹 {name}\n"
            count = 0

            for li in items:
                a_tag = li.find('a', href=re.compile(r'info/\d+/\d+'))
                if not a_tag: continue

                title = a_tag.get_text(strip=True)
                raw_href = a_tag.get('href', '')
                link = base_url + raw_href[raw_href.find('info/'):]

                li_text = li.get_text(" ", strip=True)
                date_match = re.search(r'\d{4}-\d{1,2}-\d{1,2}', li_text)

                if date_match:
                    date_str = date_match.group()
                    news_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if news_date >= start_date:
                        section_text += f"- [{date_str}] {title}  \n[查看详情]({link})\n"
                        count += 1
                        found_any = True

            if count > 0:
                full_report += section_text + "\n"
        except Exception as e:
            raise Exception(f"网络请求失败({name}): {e}")

    return full_report if found_any else None

# ==========================================
# 👑 腾讯云入口大门 (融合调度核心)
# ==========================================
def main_handler(event, context):
    print("🎬 云端双源学术助手与动态雷达联合调度启动...")
    
    # ------------------------------------------
    # 模块一：网易邮箱高分文献抓取与自适应翻译
    # ------------------------------------------
    print("\n--- ⏳ [任务1] 正在启动高分文献早报检索 ---")
    try:
        mail = imaplib.IMAP4_SSL("imap.163.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail._simple_command('ID', '("name" "Mac" "version" "11.0" "vendor" "Apple")')
        mail.select("INBOX", readonly=True)
        _, response = mail.search(None, 'ALL')
        email_ids = response[0].split()

        raw_papers = []
        for e_id in email_ids[-10:][::-1]:
            _, data = mail.fetch(e_id, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors='ignore')
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            pattern = r'\(impact factor:\s*([\d\.]+)\)\s*(.*?)\s*(?:PMID: \d+\s*)?doi:\s*(10\.\d{4,9}/[-._;()/:a-zA-Z0-9]+)'
            matches = re.findall(pattern, body, re.S)
            for if_val, zone, doi in matches:
                raw_papers.append({"doi": doi.strip(), "if": float(if_val), "zone": zone.strip()})
            if raw_papers: break
        mail.logout()
    except Exception as e:
        print(f"❌ 文献邮件读取失败: {e}")
        raw_papers = []

    if not raw_papers:
        print("📭 邮件中未检索到任何符合格式的文献。")
    else:
        raw_papers.sort(key=lambda x: x['if'], reverse=True)
        print(f"✅ 成功提取到 {len(raw_papers)} 篇文献。")

        wechat_markdown = f"### 📅 今日文献早报（{datetime.now().strftime('%Y-%m-%d')}）\n\n"
        for i, p in enumerate(raw_papers, 1):
            print(f"🔄 ({i}/{len(raw_papers)}) 正在交叉检索并自适应翻译 DOI: {p['doi']}")
            title, abstract = get_paper_from_pubmed(p['doi'])
            if not abstract:
                title, abstract = get_paper_from_ss(p['doi'])
            if not title: continue

            zh_title = smart_translate(title, original_fallback=title)
            zh_abstract = smart_translate(abstract, original_fallback=abstract)

            wechat_markdown += f"#### 📑 【文献 {i}】 {zh_title}\n"
            wechat_markdown += f"- 影响因子 (IF): `{p['if']}`  |  分区: `{p['zone']}`\n"
            wechat_markdown += f"- 💡 简报摘要: {zh_abstract}\n"
            wechat_markdown += f"- 🔗 [点击直接跳转官网](https://doi.org/{p['doi']})\n"
            wechat_markdown += "\n---\n\n"
            time.sleep(1)

        # 发送文献早报
        push_title = f"🎓 今日高分文献推荐 ({len(raw_papers)}篇)"
        send_pushdeer_msg(push_title, wechat_markdown)

    # ------------------------------------------
    # 模块二：安师大校园动态新闻自动化采集与重试
    # ------------------------------------------
    print("\n--- ⏳ [任务2] 正在启动安师大高校动态爬取 ---")
    max_retries = 5       # 云端最大支持重试 5 次（防止运行超时）
    retry_interval = 20   # 每次失败后等待 20 秒再试

    for attempt in range(1, max_retries + 1):
        print(f"🔄 正在进行第 {attempt}/{max_retries} 次尝试链接高校服务器...")
        try:
            report_content = get_ahnu_news_report()
            if report_content:
                if send_pushdeer_msg("安师大动态汇总报表", report_content):
                    print("✨ 安师大新闻简报送达成功！")
                    break
                else:
                    raise Exception("PushDeer接口调用未成功")
            else:
                print("📭 安师大近期无新闻动态更新，跳过推送。")
                break 

        except Exception as e:
            print(f"⚠️ 本次安师大爬取失败。原因: {e}")
            if attempt < max_retries:
                print(f"💤 正在等待网络就绪，{retry_interval} 秒后自动重试...")
                time.sleep(retry_interval)
            else:
                print("❌ 达到云端最大重试次数，安师大今日抓取彻底宣告失败。")

    print("\n🎉 [全案结束] 所有任务执行完毕，云实例正在优雅自行销毁...下期再见！")
    return "SUCCESS"

if __name__ == "__main__":
    # 在本地或 GitHub 环境下运行时，自动模拟腾讯云门禁，完美触发
    main_handler(None, None)
