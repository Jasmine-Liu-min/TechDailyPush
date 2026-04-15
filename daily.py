"""
Tech Daily - 科技日报推送工具
定时爬取 Hacker News / GitHub 热门项目 / Product Hunt
生成精美邮件推送到你的邮箱

用法：
    python daily.py              # 立即抓取并发送
    python daily.py --preview    # 只预览不发送（生成 preview.html）
    python daily.py --daemon     # 后台定时运行

依赖：无（纯标准库）
"""

import json, os, sys, time, re, smtplib, urllib.request
from datetime import datetime, date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from html import escape as esc

DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    with open(os.path.join(DIR, "config.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def api(url, timeout=10):
    req = urllib.request.Request(url, headers={
        "User-Agent": "TechDaily/1.0",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


# ===== 信源 =====

def fetch_hackernews(n=10):
    """Hacker News 首页热帖（via Algolia API，稳定可靠）"""
    print("🔶 Hacker News...")
    data = api(f"https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage={n}")
    items = []
    for h in data.get("hits", []):
        items.append({
            "title": h.get("title", ""),
            "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID','')}",
            "desc": f"⬆ {h.get('points',0)}  💬 {h.get('num_comments',0)}",
        })
    print(f"   ✓ {len(items)} 条")
    return items


def fetch_github(n=10):
    """GitHub 近期热门新项目（via Search API）"""
    print("🐙 GitHub Trending...")
    # 搜索最近7天创建的、按 star 排序的项目
    d = date.today()
    week_ago = f"{d.year}-{d.month:02d}-{max(d.day-7,1):02d}"
    data = api(f"https://api.github.com/search/repositories?q=created:>{week_ago}&sort=stars&per_page={n}")
    items = []
    for repo in data.get("items", []):
        desc = (repo.get("description") or "")[:80]
        items.append({
            "title": repo.get("full_name", ""),
            "url": repo.get("html_url", ""),
            "desc": f"⭐ {repo.get('stargazers_count',0)}  {desc}",
        })
    print(f"   ✓ {len(items)} 条")
    return items


def fetch_hn_show(n=10):
    """Hacker News Show HN（新产品展示，替代 Product Hunt）"""
    print("🚀 Show HN (新产品)...")
    data = api(f"https://hn.algolia.com/api/v1/search?tags=show_hn&hitsPerPage={n}")
    items = []
    for h in data.get("hits", []):
        title = h.get("title", "").replace("Show HN: ", "").replace("Show HN:", "")
        items.append({
            "title": title,
            "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID','')}",
            "desc": f"⬆ {h.get('points',0)}  💬 {h.get('num_comments',0)}",
        })
    print(f"   ✓ {len(items)} 条")
    return items


def fetch_hn_ask(n=5):
    """Hacker News Ask HN（热门讨论）"""
    print("💬 Ask HN (热门讨论)...")
    data = api(f"https://hn.algolia.com/api/v1/search?tags=ask_hn&hitsPerPage={n}")
    items = []
    for h in data.get("hits", []):
        title = h.get("title", "").replace("Ask HN: ", "").replace("Ask HN:", "")
        items.append({
            "title": title,
            "url": f"https://news.ycombinator.com/item?id={h.get('objectID','')}",
            "desc": f"💬 {h.get('num_comments',0)}",
        })
    print(f"   ✓ {len(items)} 条")
    return items


def fetch_producthunt(n=10):
    """Product Hunt 今日新产品（via Atom Feed）"""
    print("🔥 Product Hunt...")
    req = urllib.request.Request("https://www.producthunt.com/feed", headers={
        "User-Agent": "Mozilla/5.0",
    })
    with urllib.request.urlopen(req, timeout=10) as r:
        xml = r.read().decode("utf-8")
    entries = re.findall(r"<entry>(.*?)</entry>", xml, re.DOTALL)
    items = []
    for entry in entries[:n]:
        title = re.search(r"<title>(.+?)</title>", entry)
        link = re.search(r'<link[^>]*href="([^"]+)"', entry)
        desc_match = re.search(r"<content[^>]*>(.+?)</content>", entry, re.DOTALL)
        desc = ""
        if desc_match:
            raw = desc_match.group(1).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            p = re.search(r"<p>\s*(.+?)\s*</p>", raw)
            if p:
                desc = re.sub(r"<[^>]+>", "", p.group(1)).strip()
        items.append({
            "title": title.group(1) if title else "",
            "url": link.group(1) if link else "",
            "desc": desc,
        })
    print(f"   ✓ {len(items)} 条")
    return items


def fetch_36kr(n=10):
    """36氪快讯（从页面 initialState 提取）"""
    print("📰 36氪快讯...")
    req = urllib.request.Request("https://36kr.com/newsflashes", headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode("utf-8", errors="ignore")
    m = re.search(r'window\.initialState\s*=\s*(.+?);?\s*</script>', html, re.DOTALL)
    if not m:
        print("   ⚠ 未找到数据")
        return []
    d = json.loads(m.group(1).strip().rstrip(";"))
    item_list = d["newsflashCatalogData"]["data"]["newsflashList"]["data"]["itemList"]
    items = []
    for it in item_list[:n]:
        mat = it.get("templateMaterial", {})
        title = mat.get("widgetTitle", "")
        item_id = it.get("itemId", "")
        if title:
            items.append({
                "title": title,
                "url": f"https://36kr.com/newsflashes/{item_id}",
                "desc": "",
            })
    print(f"   ✓ {len(items)} 条")
    return items


def fetch_hf_papers(n=10):
    """量子位 AI 资讯（替代 HF Papers，国内可访问）"""
    print("🤖 量子位 AI 资讯...")
    req = urllib.request.Request("https://www.qbitai.com", headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode("utf-8", errors="ignore")
    matches = re.findall(
        r'<a[^>]*href="(https://www\.qbitai\.com/\d+/\d+/[^"]+)"[^>]*>([^<]{8,80})</a>', html
    )
    items, seen = [], set()
    for url, title in matches:
        t = title.strip()
        if t not in seen:
            seen.add(t)
            items.append({"title": t, "url": url, "desc": ""})
        if len(items) >= n:
            break
    print(f"   ✓ {len(items)} 条")
    return items


def fetch_sspai(n=10):
    """少数派推荐文章"""
    print("📱 少数派...")
    req = urllib.request.Request("https://sspai.com", headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode("utf-8", errors="ignore")
    # 从页面提取文章标题和链接
    items = []
    matches = re.findall(r'"title":"([^"]{5,80})"[^}]*?"id":(\d+)', html)
    seen = set()
    for title, aid in matches:
        if title in seen:
            continue
        seen.add(title)
        items.append({
            "title": title,
            "url": f"https://sspai.com/post/{aid}",
            "desc": "",
        })
        if len(items) >= n:
            break
    if not items:
        # 备用：用 RSS
        req2 = urllib.request.Request("https://sspai.com/feed", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req2, timeout=10) as r2:
            xml = r2.read().decode("utf-8")
        titles = re.findall(r"<title><!\[CDATA\[(.+?)\]\]></title>", xml)
        links = re.findall(r"<link>(https://sspai\.com/post/\d+)</link>", xml)
        for t, l in zip(titles[:n], links[:n]):
            items.append({"title": t, "url": l, "desc": ""})
    print(f"   ✓ {len(items)} 条")
    return items


# ===== 邮件 =====

def build_email(sections):
    today = date.today().strftime("%Y年%m月%d日")
    weekdays = "一二三四五六日"
    wd = weekdays[date.today().weekday()]

    sec_html = ""
    for name, icon, subtitle, items in sections:
        if not items:
            continue
        rows = ""
        for i, item in enumerate(items):
            desc = f'<span style="color:#aaa;font-size:12px;margin-left:6px">{esc(item["desc"])}</span>' if item.get("desc") else ""
            rows += f'''<tr><td style="padding:10px 0;border-bottom:1px solid #f7f7f7;font-size:14px;line-height:1.6">
                <span style="color:#ddd;margin-right:6px;font-size:12px">{i+1}</span>
                <a href="{esc(item['url'])}" style="color:#222;text-decoration:none" target="_blank">{esc(item["title"])}</a>
                {desc}
            </td></tr>'''

        sec_html += f'''<table width="100%" style="margin-bottom:28px" cellpadding="0" cellspacing="0">
            <tr><td style="padding-bottom:10px;border-bottom:2px solid #f0f0f0">
                <span style="font-size:13px;font-weight:600;color:#888;letter-spacing:0.5px">{icon} {esc(name)}</span>
                <span style="font-size:11px;color:#bbb;margin-left:8px">{esc(subtitle)}</span>
            </td></tr>{rows}</table>'''

    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,'PingFang SC','Helvetica Neue','Microsoft YaHei',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="padding:28px 12px">
<tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,0.04)">
<tr><td style="padding:32px 28px 20px;border-bottom:1px solid #f0f0f0">
    <div style="font-size:20px;font-weight:700;color:#111">☀️ Tech Daily</div>
    <div style="font-size:12px;color:#bbb;margin-top:4px">星期{wd} · {today}</div>
</td></tr>
<tr><td style="padding:24px 28px 32px">
    {sec_html}
    <div style="text-align:center;color:#ddd;font-size:11px;margin-top:16px;padding-top:12px;border-top:1px solid #f5f5f5">
        Tech Daily · Python 驱动 · 自动生成
    </div>
</td></tr>
</table>
</td></tr></table>
</body></html>'''


def send_email(cfg, html):
    e = cfg["email"]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"☀️ Tech Daily - {date.today().strftime('%m.%d')}"
    msg["From"] = e["sender"]
    msg["To"] = e["receiver"]
    msg.attach(MIMEText(html, "html", "utf-8"))
    print("📧 发送邮件...")
    with smtplib.SMTP_SSL(e["smtp_server"], e["smtp_port"]) as s:
        s.login(e["sender"], e["password"])
        s.sendmail(e["sender"], e["receiver"], msg.as_string())
    print("✅ 发送成功！")


# ===== 主流程 =====

def run(preview=False):
    cfg = load_config()
    n = cfg.get("top_n", 10)

    sections = []
    # 国内信源
    try:
        sections.append(("36氪快讯", "📰", "国内科技商业快讯", fetch_36kr(n)))
    except Exception as e:
        print(f"  ⚠ 36氪失败: {e}")

    try:
        sections.append(("量子位", "🤖", "国内 AI 行业资讯", fetch_hf_papers(n)))
    except Exception as e:
        print(f"  ⚠ 量子位失败: {e}")

    # 海外信源
    try:
        sections.append(("Product Hunt", "🔥", "全球每日新产品发布", fetch_producthunt(n)))
    except Exception as e:
        print(f"  ⚠ Product Hunt 失败: {e}")

    try:
        sections.append(("Hacker News", "🔶", "硅谷科技社区热帖", fetch_hackernews(n)))
    except Exception as e:
        print(f"  ⚠ HN 失败: {e}")

    try:
        sections.append(("Show HN", "🚀", "开发者新产品展示", fetch_hn_show(n)))
    except Exception as e:
        print(f"  ⚠ Show HN 失败: {e}")

    try:
        sections.append(("GitHub 热门", "🐙", "近期高星新开源项目", fetch_github(n)))
    except Exception as e:
        print(f"  ⚠ GitHub 失败: {e}")

    try:
        sections.append(("Ask HN", "💬", "科技圈热门讨论", fetch_hn_ask(5)))
    except Exception as e:
        print(f"  ⚠ Ask HN 失败: {e}")

    html = build_email(sections)

    if preview:
        out = os.path.join(DIR, "preview.html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\n👀 预览：{out}")
        import webbrowser
        webbrowser.open("file://" + out)
    else:
        send_email(cfg, html)


def daemon():
    cfg = load_config()
    t = cfg.get("schedule", "08:00")
    print(f"🕐 定时模式，每天 {t} 发送 (Ctrl+C 退出)")
    sent = False
    while True:
        now = datetime.now().strftime("%H:%M")
        if now == t and not sent:
            try:
                run()
            except Exception as e:
                print(f"❌ {e}")
            sent = True
        if now != t:
            sent = False
        time.sleep(30)


if __name__ == "__main__":
    if "--preview" in sys.argv:
        run(preview=True)
    elif "--daemon" in sys.argv:
        daemon()
    else:
        run()
