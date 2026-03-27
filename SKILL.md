---
name: zhihu
description: |
  知乎（Zhihu）搜索助手。通过 Python 命令搜索知乎：搜索问题/回答/文章、查看热榜、热搜词、查看用户、浏览话题、阅读全文、查看评论。
  当用户提到知乎、Zhihu、知乎搜索、知乎热榜、看知乎、搜知乎、知乎上怎么说等关键词时使用。
---

# 规则

1. **只用下面的 python3 命令。禁止用 curl、wget、httpie 或任何其他方式。**
2. Skill 目录（`SKILL_DIR`）：`~/.claude/skills/zhihu` 或 `~/.openclaw/skills/zhihu`，取实际存在的路径
3. 首次使用先运行初始化：`cd <SKILL_DIR> && bash scripts/setup.sh`

# 命令

以下是全部可用命令，`P` 代表 `python3 <SKILL_DIR>/scripts/zhihu_client.py`。

所有命令均无需登录（已内置 x-zse-96 API 签名）。

| 功能 | 命令 |
|------|------|
| 搜索 | `P search "关键词"` |
| 热榜 | `P hot` |
| 热搜词 | `P hot-queries` |
| 搜索联想 | `P suggest "关键词"` |
| 问题详情+回答 | `P question <question_id>` |
| 完整回答 | `P answer <answer_id>` |
| 完整文章 | `P article <article_id>` |
| 用户资料 | `P user <url_token>` |
| 用户高赞回答 | `P user-answers <url_token>` |
| 用户文章 | `P user-articles <url_token>` |
| 话题详情 | `P topic <topic_id>` |
| 话题精华 | `P topic-top <topic_id>` |
| 评论列表 | `P comments <answer/article> <id>` |
| 导入 Cookie | `P import-cookies` |

# Cookie 导入（可选）

如遇 403 错误，可尝试导入浏览器 Cookie 获取更多权限：

1. 用浏览器登录 zhihu.com
2. 安装 Cookie-Editor 扩展，导出 JSON
3. 保存到 `<SKILL_DIR>/cookies.json`

# 示例

```shell
P hot
P hot-queries
P search "大模型"
P article 1979502019740971887
P question 595621524
P user excited-vczh
```
