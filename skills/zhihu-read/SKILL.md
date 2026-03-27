---
name: zhihu-read
description: |
  阅读知乎回答和文章全文。当用户想看某个回答的完整内容、某篇文章全文、某个问题的详情时使用。
---

# 规则

**只用下面的 python3 命令，禁止使用 curl 或其他方式。**

`P` 代表 `python3 ~/.openclaw/skills/zhihu/scripts/zhihu_client.py`。

# 命令

| 功能 | 命令 |
|------|------|
| 问题详情+回答 | `P question <question_id>` |
| 完整回答 | `P answer <answer_id>` |
| 完整文章 | `P article <article_id>` |

`question_id`、`answer_id`、`article_id` 来自搜索结果或 URL。

# 从 URL 提取 ID

- `zhihu.com/question/12345` → question_id = 12345
- `zhihu.com/question/12345/answer/67890` → answer_id = 67890
- `zhuanlan.zhihu.com/p/12345` → article_id = 12345
