---
name: zhihu-search
description: |
  搜索知乎内容。当用户想搜索知乎上的问题、回答、文章、话题时使用。
---

# 规则

**只用下面的 python3 命令，禁止使用 curl 或其他方式。**

`P` 代表 `python3 <SKILL_DIR>/scripts/zhihu_client.py`（SKILL_DIR：`~/.claude/skills/zhihu` 或 `~/.openclaw/skills/zhihu`，取存在的路径）。

# 命令

| 功能 | 命令 |
|------|------|
| 搜索 | `P search "关键词"` |

# 展示格式

搜索结果包含问题、回答、文章、话题。每条结果展示：类型标签、标题、摘要、赞同数、链接。简洁展示，默认展示 10 条。
