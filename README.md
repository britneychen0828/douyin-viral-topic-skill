# 抖音爆款选题推荐 Skill

一个运行在 Kimi 上的 AI Skill，帮助短视频创作者每天获取个性化爆款选题建议。

**无需任何 API Key，数据完全本地，开箱即用。**

## 功能

- 自动抓取抖音热榜 TOP30，每条选题明确关联热点话题
- 分析账号风格，生成 8-10 条个性化选题建议
- 每条选题附带热点关联说明、匹配理由、拍摄建议
- 账号偏好本地持久化，下次打开直接推荐
- 随时更新账号偏好

## 安装

### 前置条件

- Kimi 已安装
- Python 3.8+

### 步骤

```bash
# 1. Clone 仓库
git clone <this-repo-url>
cd douyin-topic-recommender

# 2. 安装 Python 依赖
pip install -r scripts/requirements.txt

# 3. 将 Skill 安装到 Kimi
# 方式一：复制到 Kimi skills 目录
cp -r . ~/.kimi/skills/douyin-topic-recommender/

# 方式二：在 Kimi 中直接指向本目录（参考 Kimi 文档）
```

## 使用

在 Kimi 中，直接说：

```
帮我推荐今天的选题
```

```
根据我的账号风格，给我几个爆款选题
```

```
我做美食探店内容，今天有什么可以蹭的热点？
```

```
更新我的账号偏好，我换赛道做职场干货了
```

Skill 会自动触发，引导你完成账号设置（首次），然后抓取热榜并生成推荐。

## 数据来源

| 来源 | 说明 |
|------|------|
| 抖音热榜 | 抖音公开热词榜，取 TOP30 条 |

## 文件结构

```
douyin-topic-recommender/
├── SKILL.md                  # Skill 核心指令
├── README.md
├── scripts/
│   ├── fetch_trending.py     # 抖音热榜抓取
│   ├── analyze_account.py    # 账号公开信息分析
│   ├── manage_prefs.py       # 用户偏好管理
│   └── requirements.txt      # Python 依赖
└── references/
    └── output_format.md      # 输出格式模板
```

## 用户数据

账号偏好保存在本地 `~/.douyin_prefs.json`，不联网、不上传。

删除偏好：
```bash
python scripts/manage_prefs.py delete
```

## 网络说明

如在中国大陆境外运行，抖音热点可能受限，可手动提供热榜话题后生成选题。

## License

MIT
