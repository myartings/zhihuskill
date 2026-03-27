---
name: zhihu-comments
description: |
  查看知乎回答或文章的评论。当用户想看评论、看大家怎么说时使用。
---

# 规则

**只用下面的 python3 命令，禁止使用 curl 或其他方式。**

`P` 代表 `python3 <SKILL_DIR>/scripts/zhihu_client.py`（SKILL_DIR：`~/.claude/skills/zhihu` 或 `~/.openclaw/skills/zhihu`，取存在的路径）。

# 命令

| 功能 | 命令 |
|------|------|
| 回答评论 | `P comments answer <answer_id>` |
| 文章评论 | `P comments article <article_id>` |

ID 来自搜索结果或阅读内容时的输出。
