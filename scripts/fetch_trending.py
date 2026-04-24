#!/usr/bin/env python3
"""
热榜抓取脚本 - 多源整合（无需 API Key）
数据源优先级：抖音热点 → 微博热搜 → 百度热搜
"""

import json
import sys
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS_PC = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
}

HEADERS_MOBILE = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/16.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
}

TIMEOUT = 12


def fetch_douyin_hot() -> list[dict]:
    """抖音热点关键词榜（无鉴权公开接口）"""
    url = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"
    try:
        resp = requests.get(
            url,
            headers={**HEADERS_MOBILE, "Referer": "https://www.douyin.com/"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        topics = []
        for item in data.get("word_list", []):
            word = item.get("word", "").strip()
            if word:
                topics.append(
                    {
                        "title": word,
                        "heat": item.get("hot_value", 0),
                        "category": "抖音热榜",
                        "source": "抖音",
                    }
                )
        return topics[:25]
    except Exception as e:
        print(f"[抖音热点] 抓取失败: {e}", file=sys.stderr)
        return []


def fetch_weibo_hot() -> list[dict]:
    """微博实时热搜（JSON API，最稳定）"""
    url = "https://weibo.com/ajax/side/hotSearch"
    try:
        resp = requests.get(
            url,
            headers={**HEADERS_PC, "Referer": "https://weibo.com/"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        topics = []
        for item in data.get("data", {}).get("realtime", []):
            word = item.get("word", "").strip()
            if not word:
                continue
            topics.append(
                {
                    "title": word,
                    "heat": item.get("num", 0),
                    "category": item.get("category", "综合"),
                    "source": "微博热搜",
                }
            )
        return topics[:30]
    except Exception as e:
        print(f"[微博热搜] 抓取失败: {e}", file=sys.stderr)
        return []


def fetch_baidu_hot() -> list[dict]:
    """百度实时热搜"""
    url = "https://top.baidu.com/board?tab=realtime"
    try:
        resp = requests.get(
            url,
            headers={**HEADERS_PC, "Referer": "https://www.baidu.com/"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        topics = []
        # 百度热搜条目选择器（兼容多版本页面结构）
        selectors = [
            "div.item_1LiJJ",
            "div[class*='content_'] strong",
            "a[href*='wd='] strong",
        ]
        items = []
        for sel in selectors:
            items = soup.select(sel)
            if items:
                break

        for item in items[:20]:
            title = (
                item.get_text(strip=True)
                if item.name == "strong"
                else (item.select_one("strong") or item).get_text(strip=True)
            )
            if title:
                topics.append(
                    {"title": title, "heat": 0, "category": "综合", "source": "百度热搜"}
                )
        return topics
    except Exception as e:
        print(f"[百度热搜] 抓取失败: {e}", file=sys.stderr)
        return []


def fetch_zhihu_hot() -> list[dict]:
    """知乎热榜（长视频/深度内容创作者参考）"""
    url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=20"
    try:
        resp = requests.get(
            url,
            headers={**HEADERS_PC, "Referer": "https://www.zhihu.com/"},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        topics = []
        for item in data.get("data", []):
            title = item.get("target", {}).get("title", "").strip()
            if title:
                topics.append(
                    {"title": title, "heat": 0, "category": "知识/问答", "source": "知乎热榜"}
                )
        return topics[:15]
    except Exception as e:
        print(f"[知乎热榜] 抓取失败: {e}", file=sys.stderr)
        return []


def deduplicate(topics: list[dict]) -> list[dict]:
    """按标题前 8 字去重，保留先出现的"""
    seen: set[str] = set()
    result = []
    for t in topics:
        key = t["title"][:8]
        if key not in seen:
            seen.add(key)
            result.append(t)
    return result


def main():
    print("正在抓取实时热榜...", file=sys.stderr)

    all_topics: list[dict] = []
    source_stats: dict[str, int] = {}

    for fetcher in [fetch_douyin_hot, fetch_weibo_hot, fetch_baidu_hot, fetch_zhihu_hot]:
        items = fetcher()
        if items:
            src = items[0]["source"]
            source_stats[src] = len(items)
            all_topics.extend(items)
            print(f"  ✓ {src}：{len(items)} 条", file=sys.stderr)

    if not all_topics:
        print("所有数据源均抓取失败，请检查网络连接。", file=sys.stderr)
        sys.exit(1)

    topics = deduplicate(all_topics)

    output = {
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "sources": source_stats,
        "total": len(topics),
        "topics": topics,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
