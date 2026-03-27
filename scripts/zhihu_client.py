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
import hashlib
import random
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
ZSE_93 = "101_3_3.0"

# ── x-zse-96 Signature (SM4-based) ────────────────────────────────────────

_ZSE_INIT_STR = "6fpLRqJO8M/c3jnYxFkUVC4ZIG12SiH=5v0mXDazWBTsuw7QetbKdoPyAl+hN9rgE"
_ZSE_ZK = [
    1170614578, 1024848638, 1413669199, -343334464, -766094290, -1373058082,
    -143119608, -297228157, 1933479194, -971186181, -406453910, 460404854,
    -547427574, -1891326262, -1679095901, 2119585428, -2029270069, 2035090028,
    -1521520070, -5587175, -77751101, -2094365853, -1243052806, 1579901135,
    1321810770, 456816404, -1391643889, -229302305, 330002838, -788960546,
    363569021, -1947871109,
]
_ZSE_ZB = [
    20, 223, 245, 7, 248, 2, 194, 209, 87, 6, 227, 253, 240, 128, 222, 91,
    237, 9, 125, 157, 230, 93, 252, 205, 90, 79, 144, 199, 159, 197, 186, 167,
    39, 37, 156, 198, 38, 42, 43, 168, 217, 153, 15, 103, 80, 189, 71, 191,
    97, 84, 247, 95, 36, 69, 14, 35, 12, 171, 28, 114, 178, 148, 86, 182,
    32, 83, 158, 109, 22, 255, 94, 238, 151, 85, 77, 124, 254, 18, 4, 26,
    123, 176, 232, 193, 131, 172, 143, 142, 150, 30, 10, 146, 162, 62, 224, 218,
    196, 229, 1, 192, 213, 27, 110, 56, 231, 180, 138, 107, 242, 187, 54, 120,
    19, 44, 117, 228, 215, 203, 53, 239, 251, 127, 81, 11, 133, 96, 204, 132,
    41, 115, 73, 55, 249, 147, 102, 48, 122, 145, 106, 118, 74, 190, 29, 16,
    174, 5, 177, 129, 63, 113, 99, 31, 161, 76, 246, 34, 211, 13, 60, 68,
    207, 160, 65, 111, 82, 165, 67, 169, 225, 57, 112, 244, 155, 51, 236, 200,
    233, 58, 61, 47, 100, 137, 185, 64, 17, 70, 234, 163, 219, 108, 170, 166,
    59, 149, 52, 105, 24, 212, 78, 173, 45, 0, 116, 226, 119, 136, 206, 135,
    175, 195, 25, 92, 121, 208, 126, 139, 3, 75, 141, 21, 130, 98, 241, 40,
    154, 66, 184, 49, 181, 46, 243, 88, 101, 183, 8, 23, 72, 188, 104, 179,
    210, 134, 250, 201, 164, 89, 216, 202, 220, 50, 221, 152, 140, 33, 235, 214,
]
_M = 0xFFFFFFFF


def _u32(x):
    return x & _M


def _i32(x):
    x = x & _M
    return x - 0x100000000 if x >= 0x80000000 else x


def _put_be32(val, buf, off):
    buf[off] = (val >> 24) & 0xFF
    buf[off + 1] = (val >> 16) & 0xFF
    buf[off + 2] = (val >> 8) & 0xFF
    buf[off + 3] = val & 0xFF


def _get_be32(buf, off):
    return ((buf[off] & 0xFF) << 24 | (buf[off + 1] & 0xFF) << 16 |
            (buf[off + 2] & 0xFF) << 8 | (buf[off + 3] & 0xFF))


def _rotl32(x, n):
    x = _u32(x)
    return _u32((x << n) | (x >> (32 - n)))


def _sm4_g(e):
    t = [0] * 4
    _put_be32(_u32(e), t, 0)
    n = [_ZSE_ZB[t[0]], _ZSE_ZB[t[1]], _ZSE_ZB[t[2]], _ZSE_ZB[t[3]]]
    r = _get_be32(n, 0)
    return _i32(r ^ _rotl32(r, 2) ^ _rotl32(r, 10) ^ _rotl32(r, 18) ^ _rotl32(r, 24))


def _sm4_block(inp):
    out = [0] * 16
    n = [0] * 36
    n[0] = _i32(_get_be32(inp, 0))
    n[1] = _i32(_get_be32(inp, 4))
    n[2] = _i32(_get_be32(inp, 8))
    n[3] = _i32(_get_be32(inp, 12))
    for r in range(32):
        o = _sm4_g(_i32(n[r + 1] ^ n[r + 2] ^ n[r + 3] ^ _ZSE_ZK[r]))
        n[r + 4] = _i32(n[r] ^ o)
    _put_be32(_u32(n[35]), out, 0)
    _put_be32(_u32(n[34]), out, 4)
    _put_be32(_u32(n[33]), out, 8)
    _put_be32(_u32(n[32]), out, 12)
    return out


def _sm4_cbc(data, iv):
    result = []
    for i in range(0, len(data), 16):
        block = data[i:i + 16]
        xored = [(block[j] ^ iv[j]) & 0xFF for j in range(16)]
        iv = _sm4_block(xored)
        result.extend(iv)
    return result


def _encode_first_block(block_16):
    offset = [48, 53, 57, 48, 53, 51, 102, 55, 100, 49, 53, 101, 48, 49, 100, 55]
    xored = [((block_16[i] ^ offset[i]) ^ 42) & 0xFF for i in range(16)]
    return _sm4_block(xored)


def _encode_triplet(ar):
    b = ar[1] << 8
    c = ar[0] | b
    d = ar[2] << 16
    e = c | d
    result = [e & 63]
    x6 = 6
    while len(result) < 4:
        result.append((e >> x6) & 63)
        x6 += 6
    return result


def _compute_zse96(md5_hex):
    """Compute x-zse-96 value from MD5 hex string."""
    init_array = [ord(c) for c in md5_hex]
    init_array.insert(0, 0)
    init_array.insert(0, random.randint(0, 126))
    while len(init_array) < 48:
        init_array.append(14)

    block0 = _encode_first_block(init_array[:16])
    block_rest = _sm4_cbc(init_array[16:48], block0)
    full = block0 + block_rest

    for i in range(47, -1, -4):
        full[i] ^= 58
    full.reverse()

    encoded = []
    for j in range(3, len(full) + 1, 3):
        encoded.extend(_encode_triplet(full[j - 3:j]))

    return "".join(_ZSE_INIT_STR[idx] for idx in encoded)


def sign_request(url_path, d_c0):
    """Generate x-zse-96 header for a given API path and d_c0 cookie."""
    plaintext = f"{ZSE_93}+{url_path}+{d_c0}"
    md5_hex = hashlib.md5(plaintext.encode()).hexdigest()
    encrypted = _compute_zse96(md5_hex)
    return f"2.0_{encrypted}"


# ── Cookie Management ───────────────────────────────────────────────────────

_opener = None
_d_c0 = None


def _generate_d_c0():
    """Generate a synthetic d_c0 device cookie value."""
    import string
    import time
    rand = "".join(random.choices(string.ascii_letters + string.digits, k=20))
    return f'"A{rand}|{int(time.time())}"'


def _load_cookies():
    """Load cookies and extract d_c0 value. Auto-generate d_c0 if missing."""
    global _opener, _d_c0
    cj = http.cookiejar.CookieJar()
    _d_c0 = None

    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE) as f:
                cookies_data = json.load(f)

            for c in cookies_data:
                domain = c.get("domain", "")
                if "zhihu" not in domain:
                    continue
                name = c.get("name", "")
                value = c.get("value", "")
                if name == "d_c0":
                    _d_c0 = value
                cookie = http.cookiejar.Cookie(
                    version=0,
                    name=name,
                    value=value,
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

    # Auto-generate d_c0 if not found in cookies
    if not _d_c0:
        _d_c0 = _generate_d_c0()
        import time
        dc_cookie = http.cookiejar.Cookie(
            version=0, name="d_c0", value=_d_c0,
            port=None, port_specified=False,
            domain=".zhihu.com", domain_specified=True, domain_initial_dot=True,
            path="/", path_specified=True,
            secure=False, expires=int(time.time()) + 86400 * 365,
            discard=False, comment=None, comment_url=None, rest={},
        )
        cj.set_cookie(dc_cookie)

    _opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def get_opener():
    """Get a URL opener with cookies loaded."""
    global _opener
    if _opener is None:
        _load_cookies()
    return _opener


def get_d_c0():
    """Get d_c0 cookie value (needed for API signing)."""
    global _d_c0
    if _opener is None:
        _load_cookies()
    return _d_c0


def _do_request(url, headers):
    """Make HTTP request and return parsed JSON or error dict."""
    req = urllib.request.Request(url, headers=headers)
    try:
        opener = get_opener()
        with opener.open(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        return {"error": f"HTTP {e.code}: {body}", "_code": e.code}
    except Exception as e:
        return {"error": str(e)}


def api(path, params=None, base=None):
    url = (base or API_BASE) + path
    if params:
        url += "?" + urllib.parse.urlencode(params)

    # Try without signing first (some endpoints work without it)
    result = _do_request(url, HEADERS)
    if "_code" not in result or result["_code"] != 403:
        result.pop("_code", None)
        return result

    # 403 → retry with x-zse-96 signing
    parsed = urllib.parse.urlparse(url)
    url_path = parsed.path
    if parsed.query:
        url_path += "?" + parsed.query

    d_c0 = get_d_c0()
    headers = dict(HEADERS)
    headers["x-zse-93"] = ZSE_93
    headers["x-zse-96"] = sign_request(url_path, d_c0)

    result = _do_request(url, headers)
    code = result.pop("_code", None)
    if code == 401:
        return {"error": f"需要登录。请运行: python3 {__file__} import-cookies"}
    elif code == 403:
        return {"error": f"无权访问 (403)。请运行: python3 {__file__} import-cookies"}
    return result


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

def _search_via_duckduckgo(keyword):
    """Fallback: search zhihu content via DuckDuckGo (no login required)."""
    query = urllib.parse.quote(f"{keyword} site:zhihu.com")
    url = f"https://html.duckduckgo.com/html/?q={query}"
    req = urllib.request.Request(url, headers={
        "User-Agent": HEADERS["User-Agent"],
        "Accept": "text/html",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            page = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"搜索失败: {e}")
        return

    # Extract results: links and titles
    results = re.findall(
        r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>(.*?)</a>',
        page,
    )
    snippets = re.findall(
        r'<a class="result__snippet"[^>]*>(.*?)</a>',
        page,
        re.DOTALL,
    )

    if not results:
        print("未找到相关结果，请尝试其他关键词")
        return

    print(f"搜索「{keyword}」结果:\n")
    count = 0
    for i, (raw_link, raw_title) in enumerate(results):
        title = strip_html(raw_title)
        snippet = strip_html(snippets[i]) if i < len(snippets) else ""

        # Extract real URL from DuckDuckGo redirect
        m = re.search(r'uddg=([^&]+)', raw_link)
        link = urllib.parse.unquote(m.group(1)) if m else raw_link

        # Skip ads and non-zhihu results
        if "zhihu.com" not in link:
            continue

        count += 1
        if count > 15:
            break

        # Determine type from URL
        if "zhuanlan.zhihu.com/p/" in link:
            tag = "文章"
        elif "/answer/" in link:
            tag = "回答"
        elif "/question/" in link:
            tag = "问题"
        else:
            tag = "知乎"

        print(f"{count}. [{tag}] {title}")
        if snippet:
            print(f"   {truncate(snippet, 150)}")
        print(f"   {link}")
        print()


def _search_via_api(keyword):
    """Search via Zhihu API (requires login cookie)."""
    r = api("/search_v3", {
        "t": "general",
        "q": keyword,
        "correction": 1,
        "offset": 0,
        "limit": 10,
    })
    if "error" in r:
        return False

    data = r.get("data", [])
    if not data:
        return False

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
    return True


def cmd_search(keyword):
    # Try Zhihu API first (if cookies available), fallback to DuckDuckGo
    if os.path.exists(COOKIE_FILE) and _search_via_api(keyword):
        return
    _search_via_duckduckgo(keyword)


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
