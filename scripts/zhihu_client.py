#!/usr/bin/env python3
"""Zhihu (知乎) CLI Client.

Usage:
    python zhihu_client.py search <keyword>           # Search Zhihu
    python zhihu_client.py hot                        # Trending / hot list
    python zhihu_client.py hot-queries                # Hot search queries
    python zhihu_client.py suggest <keyword>          # Search suggestions
    python zhihu_client.py question <question_id>     # Question detail + top answers
    python zhihu_client.py answer <answer_id>         # Full answer content
    python zhihu_client.py article <article_id>       # Full article content
    python zhihu_client.py user <url_token>           # User profile
    python zhihu_client.py user-answers <url_token>   # User's top answers
    python zhihu_client.py user-articles <url_token>  # User's articles
    python zhihu_client.py topic <topic_id>           # Topic detail
    python zhihu_client.py topic-top <topic_id>       # Top answers under topic
    python zhihu_client.py comments <type> <id>       # Comments (type: answer/article)
    python zhihu_client.py import-cookies             # Import cookies from browser

Cookies: Reads from ~/.openclaw/skills/zhihu/cookies.json (Netscape/JSON format).
Some features (search, hot list, reading answers) require login cookies.
"""

import sys
import os
import json
import re
import html
import http.cookiejar
import urllib.request
import urllib.error
import urllib.parse

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIE_FILE = os.path.join(SKILL_DIR, "cookies.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.zhihu.com/",
    "Accept": "application/json",
}

API_BASE = "https://www.zhihu.com/api/v4"

# ── Cookie Management ───────────────────────────────────────────────────────

_opener = None


def get_opener():
    """Get a URL opener with cookies loaded."""
    global _opener
    if _opener is not None:
        return _opener

    cj = http.cookiejar.CookieJar()

    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE) as f:
                cookies_data = json.load(f)

            for c in cookies_data:
                domain = c.get("domain", "")
                if "zhihu" not in domain:
                    continue
                cookie = http.cookiejar.Cookie(
                    version=0,
                    name=c.get("name", ""),
                    value=c.get("value", ""),
                    port=None,
                    port_specified=False,
                    domain=domain,
                    domain_specified=True,
                    domain_initial_dot=domain.startswith("."),
                    path=c.get("path", "/"),
                    path_specified=True,
                    secure=c.get("secure", False),
                    expires=int(c.get("expirationDate", 0) or 0),
                    discard=False,
                    comment=None,
                    comment_url=None,
                    rest={"HttpOnly": str(c.get("httpOnly", False))},
                )
                cj.set_cookie(cookie)
        except Exception as e:
            print(f"警告: 加载 cookies 失败: {e}", file=sys.stderr)

    _opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    return _opener


def api(path, params=None, base=None):
    url = (base or API_BASE) + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        opener = get_opener()
        with opener.open(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        code = e.code
        if code == 401:
            return {"error": f"需要登录。请运行: python3 {__file__} import-cookies"}
        elif code == 403:
            return {"error": f"无权访问 (403)。可能需要登录或 Cookie 已过期。"}
        return {"error": f"HTTP {code}: {body}"}
    except Exception as e:
        return {"error": str(e)}


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return text.strip()


def truncate(text, length=200):
    text = text.replace("\n", " ")
    if len(text) > length:
        return text[:length] + "..."
    return text


def check_error(r):
    if "error" in r:
        print(f"错误: {r['error']}")
        return True
    return False


# ── Import Cookies ──────────────────────────────────────────────────────────

def cmd_import_cookies():
    """Guide user to import cookies."""
    print("=== 导入知乎 Cookies ===\n")
    print("方法 1: 使用浏览器扩展 (推荐)")
    print("  1. 安装 'Cookie-Editor' 或 'EditThisCookie' 浏览器扩展")
    print("  2. 登录 zhihu.com")
    print("  3. 点击扩展图标 → Export (JSON 格式)")
    print(f"  4. 将导出的 JSON 保存到: {COOKIE_FILE}")
    print()
    print("方法 2: 手动从 DevTools 导出")
    print("  1. 登录 zhihu.com")
    print("  2. 打开 DevTools (F12) → Application → Cookies")
    print("  3. 复制所有 zhihu.com 的 cookies")
    print(f"  4. 保存为 JSON 数组到: {COOKIE_FILE}")
    print()
    print("JSON 格式示例:")
    print('[{"name": "z_c0", "value": "...", "domain": ".zhihu.com", "path": "/"}]')
    print()
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE) as f:
                data = json.load(f)
            zhihu = [c for c in data if "zhihu" in c.get("domain", "")]
            print(f"当前状态: cookies.json 已存在，含 {len(zhihu)} 个知乎 cookie")
            key_cookies = [c["name"] for c in zhihu if c["name"] in ("z_c0", "d_c0", "_xsrf")]
            if key_cookies:
                print(f"  关键 cookie: {', '.join(key_cookies)}")
            if "z_c0" not in key_cookies:
                print("  ⚠ 缺少 z_c0 (登录 token)，大部分功能将不可用")
        except Exception as e:
            print(f"当前状态: cookies.json 存在但读取失败: {e}")
    else:
        print(f"当前状态: cookies.json 不存在")


# ── Search ──────────────────────────────────────────────────────────────────

def cmd_search(keyword):
    r = api("/search_v3", {
        "t": "general",
        "q": keyword,
        "correction": 1,
        "offset": 0,
        "limit": 10,
    })
    if check_error(r):
        return

    data = r.get("data", [])
    if not data:
        print("未找到相关结果，请尝试其他关键词")
        return

    print(f"搜索「{keyword}」结果:\n")
    count = 0
    for item in data:
        obj = item.get("object", {})
        obj_type = obj.get("type", "")
        highlight = item.get("highlight", {})

        title = strip_html(highlight.get("title", "") or obj.get("title", "") or obj.get("name", ""))
        desc = strip_html(highlight.get("description", "") or obj.get("excerpt", "") or obj.get("content", ""))

        if not title and not desc:
            continue

        count += 1
        if obj_type == "answer":
            qid = obj.get("question", {}).get("id", "")
            aid = obj.get("id", "")
            author = obj.get("author", {}).get("name", "匿名")
            voteup = obj.get("voteup_count", 0)
            comment = obj.get("comment_count", 0)
            q_title = strip_html(obj.get("question", {}).get("title", title))
            print(f"{count}. [回答] {q_title}")
            print(f"   {truncate(desc)}")
            print(f"   作者: {author}  赞同: {voteup}  评论: {comment}")
            print(f"   https://www.zhihu.com/question/{qid}/answer/{aid}")
        elif obj_type == "article":
            aid = obj.get("id", "")
            author = obj.get("author", {}).get("name", "匿名")
            voteup = obj.get("voteup_count", 0)
            print(f"{count}. [文章] {title}")
            print(f"   {truncate(desc)}")
            print(f"   作者: {author}  赞同: {voteup}")
            print(f"   https://zhuanlan.zhihu.com/p/{aid}")
        elif obj_type == "question":
            qid = obj.get("id", "")
            answer_count = obj.get("answer_count", 0)
            follower = obj.get("follower_count", 0)
            print(f"{count}. [问题] {title}")
            print(f"   {truncate(desc)}")
            print(f"   回答: {answer_count}  关注: {follower}")
            print(f"   https://www.zhihu.com/question/{qid}")
        elif obj_type == "topic":
            tid = obj.get("id", "")
            print(f"{count}. [话题] {title}")
            if desc:
                print(f"   {truncate(desc)}")
            print(f"   https://www.zhihu.com/topic/{tid}")
        else:
            print(f"{count}. [{obj_type or '其他'}] {title}")
            if desc:
                print(f"   {truncate(desc)}")
        print()


# ── Hot List ────────────────────────────────────────────────────────────────

def cmd_hot():
    # Try creators rank hot (works without auth)
    r = api("/creators/rank/hot", {
        "domain": "0",
        "period": "hour",
        "limit": 50,
        "offset": 0,
    })
    if check_error(r):
        return

    data = r.get("data", [])
    if not data:
        print("暂无热榜数据")
        return

    print("知乎热榜:\n")
    for i, item in enumerate(data, 1):
        question = item.get("question", item.get("target", {}))
        title = question.get("title", "")
        qid = question.get("id", "") or question.get("token", "")
        topics = question.get("topics", [])
        topic_names = ", ".join(t.get("name", "") for t in topics[:3]) if topics else ""

        print(f"{i}. {title}")
        if topic_names:
            print(f"   话题: {topic_names}")
        if qid:
            print(f"   https://www.zhihu.com/question/{qid}")
        print()


def cmd_hot_queries():
    r = api("/search/hot_search")
    if check_error(r):
        return

    queries = r.get("hot_search_queries", r.get("data", []))
    if not queries:
        print("暂无热搜数据")
        return

    print("知乎热搜词:\n")
    for i, item in enumerate(queries, 1):
        query = item.get("query", item.get("display_query", ""))
        hot = item.get("hot_show", item.get("hot", ""))
        print(f"{i}. {query}  (热度: {hot})")
    print()


# ── Suggest ─────────────────────────────────────────────────────────────────

def cmd_suggest(keyword):
    r = api("/search/suggest", {"q": keyword, "limit": 10})
    if check_error(r):
        return

    suggestions = r.get("suggest", [])
    if not suggestions:
        print("无联想建议")
        return

    print(f"「{keyword}」相关搜索:\n")
    for i, s in enumerate(suggestions, 1):
        query = s.get("query", "")
        print(f"  {i}. {query}")
    print()


# ── Question Detail ─────────────────────────────────────────────────────────

def cmd_question(question_id):
    r = api(f"/questions/{question_id}", {
        "include": "detail,answer_count,follower_count,visit_count",
    })
    if check_error(r):
        return

    title = r.get("title", "")
    detail = strip_html(r.get("detail", ""))
    answer_count = r.get("answer_count", 0)
    follower_count = r.get("follower_count", 0)
    visit_count = r.get("visit_count", 0)

    print(f"问题: {title}")
    print(f"回答: {answer_count}  关注: {follower_count}  浏览: {visit_count}")
    if detail:
        print(f"\n{detail}")
    print(f"\nhttps://www.zhihu.com/question/{question_id}")
    print("\n" + "=" * 60)

    # Get top answers
    r2 = api(f"/questions/{question_id}/answers", {
        "include": "content,voteup_count,comment_count",
        "limit": 5,
        "sort_by": "default",
    })
    if "error" not in r2:
        answers = r2.get("data", [])
        if answers:
            print(f"\n前 {len(answers)} 个回答:\n")
            for i, a in enumerate(answers, 1):
                author = a.get("author", {}).get("name", "匿名")
                voteup = a.get("voteup_count", 0)
                comment = a.get("comment_count", 0)
                content = strip_html(a.get("content", ""))
                aid = a.get("id", "")

                print(f"── 回答 {i} ──")
                print(f"作者: {author}  赞同: {voteup}  评论: {comment}")
                print(f"{truncate(content, 500)}")
                print(f"ID: {aid}")
                print()


# ── Full Answer ─────────────────────────────────────────────────────────────

def cmd_answer(answer_id):
    r = api(f"/answers/{answer_id}", {
        "include": "content,voteup_count,comment_count,question",
    })
    if check_error(r):
        return

    question = r.get("question", {})
    q_title = question.get("title", "")
    qid = question.get("id", "")
    author = r.get("author", {}).get("name", "匿名")
    voteup = r.get("voteup_count", 0)
    comment = r.get("comment_count", 0)
    content = strip_html(r.get("content", ""))

    print(f"问题: {q_title}")
    print(f"作者: {author}  赞同: {voteup}  评论: {comment}")
    print(f"https://www.zhihu.com/question/{qid}/answer/{answer_id}")
    print("\n" + "=" * 60 + "\n")
    print(content)


# ── Full Article ────────────────────────────────────────────────────────────

def cmd_article(article_id):
    r = api(f"/articles/{article_id}")
    if check_error(r):
        return

    title = r.get("title", "")
    author = r.get("author", {}).get("name", "匿名")
    voteup = r.get("voteup_count", 0)
    comment = r.get("comment_count", 0)
    content = strip_html(r.get("content", ""))

    print(f"文章: {title}")
    print(f"作者: {author}  赞同: {voteup}  评论: {comment}")
    print(f"https://zhuanlan.zhihu.com/p/{article_id}")
    print("\n" + "=" * 60 + "\n")
    print(content)


# ── User Profile ────────────────────────────────────────────────────────────

def cmd_user(url_token):
    r = api(f"/members/{url_token}", {
        "include": "locations,employments,educations,description,business,voteup_count,thanked_count,follower_count,following_count,answer_count,articles_count",
    })
    if check_error(r):
        return

    name = r.get("name", "")
    headline = r.get("headline", "")
    desc = r.get("description", "")
    follower = r.get("follower_count", 0)
    following = r.get("following_count", 0)
    answer_count = r.get("answer_count", 0)
    article_count = r.get("articles_count", 0)
    voteup = r.get("voteup_count", 0)
    thanked = r.get("thanked_count", 0)

    locations = r.get("locations", [])
    loc = ", ".join(l.get("name", "") for l in locations) if locations else ""
    employments = r.get("employments", [])
    emp = ", ".join(
        (e.get("company", {}).get("name", "") + " " + e.get("job", {}).get("name", "")).strip()
        for e in employments
    ) if employments else ""
    educations = r.get("educations", [])
    edu = ", ".join(e.get("school", {}).get("name", "") for e in educations) if educations else ""

    print(f"{name}")
    if headline:
        print(f"  {headline}")
    if desc:
        print(f"  简介: {desc}")
    if loc:
        print(f"  所在地: {loc}")
    if emp:
        print(f"  职业: {emp}")
    if edu:
        print(f"  教育: {edu}")
    print(f"  关注: {following}  粉丝: {follower}")
    print(f"  回答: {answer_count}  文章: {article_count}")
    print(f"  获赞: {voteup}  感谢: {thanked}")
    print(f"  https://www.zhihu.com/people/{url_token}")


# ── User Answers ────────────────────────────────────────────────────────────

def cmd_user_answers(url_token):
    r = api(f"/members/{url_token}/answers", {
        "include": "content,voteup_count,comment_count",
        "limit": 10,
        "offset": 0,
        "sort_by": "voteup_count",
    })
    if check_error(r):
        return

    data = r.get("data", [])
    if not data:
        print("该用户没有公开回答")
        return

    print(f"用户 {url_token} 的高赞回答:\n")
    for i, a in enumerate(data, 1):
        q = a.get("question", {})
        q_title = q.get("title", "")
        qid = q.get("id", "")
        aid = a.get("id", "")
        voteup = a.get("voteup_count", 0)
        comment = a.get("comment_count", 0)
        content = strip_html(a.get("content", ""))

        print(f"{i}. {q_title}")
        print(f"   {truncate(content)}")
        print(f"   赞同: {voteup}  评论: {comment}")
        print(f"   https://www.zhihu.com/question/{qid}/answer/{aid}")
        print()


# ── User Articles ───────────────────────────────────────────────────────────

def cmd_user_articles(url_token):
    r = api(f"/members/{url_token}/articles", {
        "include": "content,voteup_count,comment_count",
        "limit": 10,
        "offset": 0,
        "sort_by": "voteup_count",
    })
    if check_error(r):
        return

    data = r.get("data", [])
    if not data:
        print("该用户没有公开文章")
        return

    print(f"用户 {url_token} 的文章:\n")
    for i, a in enumerate(data, 1):
        title = a.get("title", "")
        aid = a.get("id", "")
        voteup = a.get("voteup_count", 0)
        comment = a.get("comment_count", 0)
        excerpt = strip_html(a.get("excerpt", "") or a.get("content", ""))

        print(f"{i}. {title}")
        print(f"   {truncate(excerpt)}")
        print(f"   赞同: {voteup}  评论: {comment}")
        print(f"   https://zhuanlan.zhihu.com/p/{aid}")
        print()


# ── Topic ───────────────────────────────────────────────────────────────────

def cmd_topic(topic_id):
    r = api(f"/topics/{topic_id}")
    if check_error(r):
        return

    name = r.get("name", "")
    intro = strip_html(r.get("introduction", ""))
    followers = r.get("followers_count", 0)
    questions = r.get("questions_count", 0)

    print(f"话题: {name}")
    if intro:
        print(f"  {intro}")
    print(f"  关注者: {followers}  问题数: {questions}")
    print(f"  https://www.zhihu.com/topic/{topic_id}")


def cmd_topic_top(topic_id):
    r = api(f"/topics/{topic_id}/feeds/top_activity", {
        "limit": 10,
        "offset": 0,
    })
    if check_error(r):
        return

    data = r.get("data", [])
    if not data:
        print("该话题下暂无内容")
        return

    print(f"话题精华内容:\n")
    for i, item in enumerate(data, 1):
        target = item.get("target", {})
        t_type = target.get("type", "")
        title = target.get("title", "") or target.get("question", {}).get("title", "")
        excerpt = strip_html(target.get("excerpt", "") or target.get("content", ""))
        author = target.get("author", {}).get("name", "")
        voteup = target.get("voteup_count", 0)

        print(f"{i}. [{t_type}] {title}")
        if excerpt:
            print(f"   {truncate(excerpt)}")
        if author:
            print(f"   作者: {author}  赞同: {voteup}")
        print()


# ── Comments ────────────────────────────────────────────────────────────────

def cmd_comments(target_type, target_id):
    r = api(f"/{target_type}s/{target_id}/root_comments", {
        "limit": 10,
        "offset": 0,
        "order": "normal",
        "status": "open",
    })
    if check_error(r):
        return

    data = r.get("data", [])
    if not data:
        print("暂无评论")
        return

    print(f"评论列表:\n")
    for i, c in enumerate(data, 1):
        author = c.get("author", {}).get("member", {}).get("name", "匿名")
        content = strip_html(c.get("content", ""))
        vote = c.get("vote_count", 0)

        print(f"{i}. [{author}] {content}")
        print(f"   赞: {vote}")
        print()


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "search": (cmd_search, 1),
        "hot": (cmd_hot, 0),
        "hot-queries": (cmd_hot_queries, 0),
        "suggest": (cmd_suggest, 1),
        "question": (cmd_question, 1),
        "answer": (cmd_answer, 1),
        "article": (cmd_article, 1),
        "user": (cmd_user, 1),
        "user-answers": (cmd_user_answers, 1),
        "user-articles": (cmd_user_articles, 1),
        "topic": (cmd_topic, 1),
        "topic-top": (cmd_topic_top, 1),
        "comments": (cmd_comments, 2),
        "import-cookies": (cmd_import_cookies, 0),
    }

    if cmd not in commands:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)

    func, nargs = commands[cmd]
    if len(args) < nargs:
        print(f"命令 '{cmd}' 需要 {nargs} 个参数")
        sys.exit(1)

    func(*args[:nargs])


if __name__ == "__main__":
    main()
