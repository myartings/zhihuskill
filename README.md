# zhihu-skill

知乎（Zhihu）OpenClaw Skill，让 AI 助手帮你搜知乎。

## 功能

| 功能 | 需要登录 |
|------|----------|
| 搜索问题/回答/文章 | 否 (DuckDuckGo fallback) |
| 知乎热榜 | 否 |
| 热搜词 | 否 |
| 搜索联想 | 否 |
| 用户资料 | 否 |
| 阅读回答/文章全文 | 是 |
| 查看问题详情 | 是 |
| 用户回答/文章列表 | 是 |
| 话题详情/精华 | 是 |
| 评论列表 | 是 |

## 快速开始

### 安装为 OpenClaw Skill

```bash
cd ~/.openclaw/skills/
git clone https://github.com/myartings/zhihuskill.git zhihu
```

纯 Python 3 标准库实现，零依赖，无需编译。

### 导入 Cookie（可选，解锁全部功能）

知乎大部分 API 需要登录态。导入浏览器 Cookie 即可使用全部功能：

1. 用浏览器登录 [zhihu.com](https://www.zhihu.com)
2. 安装 [Cookie-Editor](https://cookie-editor.com/) 浏览器扩展
3. 点击扩展图标 → Export → JSON
4. 保存到 `~/.openclaw/skills/zhihu/cookies.json`

关键 Cookie 是 `z_c0`（登录 token），没有它大部分功能不可用。

### 使用方式

启动 OpenClaw 后，直接对话即可：

- "知乎热榜" → 热门话题
- "知乎上在搜什么" → 热搜词
- "搜一下知乎上关于大模型的讨论" → 搜索
- "看看这个知乎用户" → 用户资料
- "帮我看看这个知乎问题" → 问题详情
- "这篇知乎文章说了什么" → 文章全文

### 命令行直接使用

```bash
P=~/.openclaw/skills/zhihu/scripts/zhihu_client.py

# 无需登录
python3 $P hot                    # 热榜
python3 $P hot-queries            # 热搜词
python3 $P suggest "人工智能"      # 搜索联想
python3 $P user excited-vczh      # 用户资料

# 需要 Cookie
python3 $P search "大模型"         # 搜索
python3 $P question 1234567       # 问题详情 + 前 5 个回答
python3 $P answer 1234567         # 完整回答
python3 $P article 1234567        # 完整文章
python3 $P user-answers vczh      # 用户高赞回答
python3 $P user-articles vczh     # 用户文章
python3 $P topic 19550517         # 话题详情
python3 $P topic-top 19550517     # 话题精华
python3 $P comments answer 123    # 回答评论
python3 $P comments article 123   # 文章评论
python3 $P import-cookies         # 查看 Cookie 导入指南
```

## 项目结构

```
├── SKILL.md                         # OpenClaw 根 skill
├── skills/                          # 6 个 OpenClaw 子 skill
│   ├── zhihu-search/SKILL.md        #   搜索
│   ├── zhihu-hot/SKILL.md           #   热榜
│   ├── zhihu-user/SKILL.md          #   用户
│   ├── zhihu-topic/SKILL.md         #   话题
│   ├── zhihu-read/SKILL.md          #   阅读全文
│   └── zhihu-comments/SKILL.md      #   评论
├── scripts/
│   ├── zhihu_client.py              # 知乎 API 客户端
│   └── setup.sh                     # 初始化脚本
├── README.md
└── LICENSE
```

## 技术说明

- 纯 Python 3 标准库实现，无第三方依赖
- 使用知乎 API (`www.zhihu.com/api/v4`)
- Cookie 从 `cookies.json` 加载，兼容 Cookie-Editor 导出格式
- 所有 API 调用为只读，不会修改任何数据

## License

MIT
