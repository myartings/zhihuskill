# zhihu-skill

知乎（Zhihu）OpenClaw Skill，让 AI 助手帮你搜知乎。

## 功能

| 功能 | 需要登录 | 说明 |
|------|----------|------|
| 搜索问题/回答/文章 | 否 | Brave Search → 搜狗 → DuckDuckGo 多通道 |
| 知乎热榜 | 否 | |
| 热搜词 | 否 | |
| 搜索联想 | 否 | |
| 用户资料 | 否 | |
| 阅读回答全文 | 部分 | 无 Cookie 可读截断内容，有 Cookie 读全文 |
| 阅读文章全文 | 是 | 专栏文章需要登录 Cookie |
| 查看问题详情 | 否 | 含前 5 个回答摘要 |
| 用户回答/文章列表 | 否 | |
| 话题详情/精华 | 否 | |
| 评论列表 | 否 | |

**多通道降级**：v4 API → 移动端 API (`api.zhihu.com`) → 页面 HTML 提取，最大化无 Cookie 可用性。

## 快速开始

### 安装为 OpenClaw Skill

```bash
cd ~/.openclaw/skills/
git clone https://github.com/myartings/zhihuskill.git zhihu
```

纯 Python 3 标准库实现，零依赖，无需编译。

### 导入 Cookie（可选，解锁完整内容）

无 Cookie 也能用大部分功能（搜索、热榜、问题详情、回答截断版等）。导入 Cookie 后可读取回答/文章完整正文。

1. 用浏览器登录 [zhihu.com](https://www.zhihu.com)
2. 安装 [Cookie-Editor](https://cookie-editor.com/) 浏览器扩展
3. 点击扩展图标 → Export → JSON
4. 保存到 `~/.config/zhihu/cookies.json`

关键 Cookie 是 `z_c0`（登录 token）。

**Cookie 查找顺序**（先找到的优先）：

| 优先级 | 路径 | 说明 |
|--------|------|------|
| 1 | `$ZHIHU_COOKIE_FILE` | 环境变量指定 |
| 2 | `~/.config/zhihu/cookies.json` | 共享路径（推荐，所有 Agent 共用） |
| 3 | `<skill目录>/cookies.json` | Skill 本地，向后兼容 |

推荐使用共享路径，这样 Hermes、OpenClaw、Claude Code、Codex 等多个 Agent 只需维护一份 Cookie。

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
python3 $P search "大模型"         # 搜索（Brave/搜狗/DDG 多通道）
python3 $P suggest "人工智能"      # 搜索联想
python3 $P question 1234567       # 问题详情 + 前 5 个回答
python3 $P answer 1234567         # 回答（无 Cookie 为截断版）
python3 $P user excited-vczh      # 用户资料
python3 $P user-answers vczh      # 用户高赞回答
python3 $P user-articles vczh     # 用户文章
python3 $P topic 19550517         # 话题详情
python3 $P topic-top 19550517     # 话题精华
python3 $P comments answer 123    # 回答评论
python3 $P comments article 123   # 文章评论

# 需要 Cookie（完整内容）
python3 $P answer 1234567         # 回答全文
python3 $P article 1234567        # 文章全文
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
- 多通道降级：`www.zhihu.com/api/v4`（签名） → `api.zhihu.com`（移动端） → 页面 HTML 提取
- 内置 x-zse-96 签名算法（SM4 加密）
- Cookie 从共享路径 `~/.config/zhihu/cookies.json` 加载，兼容 Cookie-Editor 导出格式
- 所有 API 调用为只读，不会修改任何数据

## License

MIT
