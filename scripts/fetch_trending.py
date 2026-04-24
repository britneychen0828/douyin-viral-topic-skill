#!/usr/bin/env python3
"""
抖音热榜抓取脚本（无需 API Key）
"""

import json
import sys
import requests
from datetime import datetime

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
    """抖音热点关键词榜（无鉴权公开接口），取前30条"""
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
        return topics[:30]
    except Exception as e:
        print(f"[抖音热点] 抓取失败: {e}", file=sys.stderr)
        return []


def main():
    print("正在抓取抖音热榜...", file=sys.stderr)

    topics = fetch_douyin_hot()
    if not topics:
        print("抖音热榜抓取失败，请检查网络连接。", file=sys.stderr)
        sys.exit(1)

    print(f"  ✓ 抖音热榜：{len(topics)} 条", file=sys.stderr)

    output = {
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": "抖音热榜",
        "total": len(topics),
        "topics": topics,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
