---
name: zhihu-topic
description: |
  浏览知乎话题。当用户想了解某个话题的介绍、关注情况、精华内容时使用。
---

# 规则

**只用下面的 python3 命令，禁止使用 curl 或其他方式。**

`P` 代表 `python3 ~/.openclaw/skills/zhihu/scripts/zhihu_client.py`。

# 命令

| 功能 | 命令 |
|------|------|
| 话题详情 | `P topic <topic_id>` |
| 话题精华 | `P topic-top <topic_id>` |

# 流程

查看某个话题：
1. 先用 `P search "话题名"` 搜索，找到话题的 ID
2. 用 `P topic <topic_id>` 查看话题详情
3. 用 `P topic-top <topic_id>` 查看话题下精华内容
