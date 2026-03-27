# Zhihu Skill

知乎 OpenClaw Skill。

## 架构

- 纯 Python 3 标准库，无第三方依赖
- 使用知乎公开 API (`https://www.zhihu.com/api/v4`)
- 无需登录，所有功能均为只读公开内容
- CLI 客户端：`scripts/zhihu_client.py`

## 项目结构

```
├── SKILL.md                         # OpenClaw 根 skill
├── skills/                          # 6 个子 skill
├── scripts/zhihu_client.py          # 知乎 API 客户端
├── scripts/setup.sh                 # 初始化脚本
```

## 知乎 API 注意事项

- API Base: `https://www.zhihu.com/api/v4`
- 必须带 User-Agent 和 Referer header，否则返回 403
- 大部分 API 需要 `x-zse-96` 签名头（SM4 加密算法），已在客户端内置实现
- `x-zse-96` 计算流程：`md5(x-zse-93 + url_path + d_c0)` → SM4 加密 → `"2.0_" + result`
- `d_c0` cookie 如未提供会自动生成合成值
- 搜索接口 `/search_v3` 的 `t` 参数控制类型：general/topic/people
- 热榜有多个接口，优先用 `/v3/feed/topstory/hot-lists/total`
- 回答/文章内容是 HTML 格式，需 strip tags
- url_token 是用户唯一标识（非昵称），在用户主页 URL 中
