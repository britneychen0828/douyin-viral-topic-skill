#!/usr/bin/env python3
"""
抖音账号公开信息抓取
用法: python analyze_account.py "<douyin_url>"

只访问公开页面，无需登录。
由于抖音大量使用 JS 渲染，本脚本尽力提取 meta/og 信息，
信息不完整时交由 Claude 结合用户手动描述综合分析。
"""

import json
import re
import sys
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/16.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.douyin.com/",
}

TIMEOUT = 15


def normalize_url(url: str) -> str:
    url = url.strip()
    if url.startswith("http"):
        return url
    if url.startswith("@"):
        return f"https://www.douyin.com/user/{url[1:]}"
    # 纯 UID
    return f"https://www.douyin.com/user/{url}"


def extract_uid(url: str) -> str:
    for pattern in [
        r"douyin\.com/user/([A-Za-z0-9_\-]+)",
        r"v\.douyin\.com/([A-Za-z0-9]+)",
        r"@([A-Za-z0-9_一-龥]+)",
    ]:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return url


def fetch_public_info(url: str) -> dict:
    """抓取账号公开 meta 信息"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        info: dict = {}

        # Open Graph 元标签（最可靠）
        for prop in ["og:title", "og:description", "og:image"]:
            tag = soup.find("meta", property=prop)
            if tag and tag.get("content"):
                key = prop.split(":")[1]
                info[key] = tag["content"].strip()

        # Twitter Card 作为补充
        for name in ["twitter:title", "twitter:description"]:
            tag = soup.find("meta", attrs={"name": name})
            if tag and tag.get("content") and name.split(":")[1] not in info:
                info[name.split(":")[1]] = tag["content"].strip()

        # 尝试从 <script> 提取结构化数据
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, dict) and data.get("@type") in ("Person", "ProfilePage"):
                    if data.get("name"):
                        info.setdefault("title", data["name"])
                    if data.get("description"):
                        info.setdefault("description", data["description"])
            except Exception:
                pass

        return info

    except requests.RequestException as e:
        print(f"网络请求失败: {e}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"解析失败: {e}", file=sys.stderr)
        return {}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "请提供账号 URL，例如: python analyze_account.py <url>"},
                         ensure_ascii=False))
        sys.exit(1)

    raw_url = sys.argv[1]
    url = normalize_url(raw_url)
    uid = extract_uid(url)

    print(f"正在分析账号: {url}", file=sys.stderr)

    public_info = fetch_public_info(url)

    result = {
        "url": url,
        "uid": uid,
        "public_info": public_info,
        "info_complete": bool(public_info.get("title") or public_info.get("description")),
        "note": (
            "已获取账号公开信息，请结合用户描述综合分析风格。"
            if public_info
            else "未能抓取到有效信息（抖音 JS 渲染限制），请依赖用户手动描述账号风格。"
        ),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
