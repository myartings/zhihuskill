---
name: zhihu-user
description: |
  查看知乎用户资料和内容。当用户想看某人的知乎主页、回答、文章时使用。
---

# 规则

**只用下面的 python3 命令，禁止使用 curl 或其他方式。**

`P` 代表 `python3 ~/.openclaw/skills/zhihu/scripts/zhihu_client.py`。

# 命令

| 功能 | 命令 |
|------|------|
| 用户资料 | `P user <url_token>` |
| 用户高赞回答 | `P user-answers <url_token>` |
| 用户文章 | `P user-articles <url_token>` |

`url_token` 是知乎用户链接中的标识，例如 `https://www.zhihu.com/people/excited-vczh` 中的 `excited-vczh`。

如果用户提供的是昵称而非 url_token，先用 `P search "昵称"` 搜索找到 url_token。

# 展示格式

资料展示：昵称、一句话介绍、简介、所在地、职业、教育、关注数、粉丝数、获赞数、回答数、文章数。
