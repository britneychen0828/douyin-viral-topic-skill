#!/usr/bin/env python3
"""
用户偏好管理
存储位置: ~/.douyin_prefs.json
用法:
  python manage_prefs.py load          # 读取偏好
  python manage_prefs.py save          # 从 stdin 读 JSON 并保存
  python manage_prefs.py delete        # 清除偏好
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PREFS_FILE = Path.home() / ".douyin_prefs.json"


def load_prefs():
    if PREFS_FILE.exists():
        try:
            data = json.loads(PREFS_FILE.read_text(encoding="utf-8"))
            data["exists"] = True
            return data
        except Exception as e:
            print(f"读取偏好失败: {e}", file=sys.stderr)
    return {"exists": False}


def save_prefs(prefs: dict):
    prefs["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    PREFS_FILE.write_text(
        json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"偏好已保存至 {PREFS_FILE}", file=sys.stderr)
    return {"success": True, "path": str(PREFS_FILE)}


def delete_prefs():
    if PREFS_FILE.exists():
        PREFS_FILE.unlink()
        return {"success": True, "message": "偏好已清除"}
    return {"success": False, "message": "未找到已保存的偏好"}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "load"

    if cmd == "load":
        print(json.dumps(load_prefs(), ensure_ascii=False, indent=2))

    elif cmd == "save":
        raw = sys.stdin.read().strip()
        try:
            prefs = json.loads(raw)
        except json.JSONDecodeError as e:
            print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
            sys.exit(1)
        print(json.dumps(save_prefs(prefs), ensure_ascii=False))

    elif cmd == "delete":
        print(json.dumps(delete_prefs(), ensure_ascii=False))

    else:
        print(f"未知命令: {cmd}，支持 load / save / delete", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
