#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== 知乎 Skill 初始化 ==="

# 创建 ~/.openclaw/skills/zhihu 软链接（兼容 SKILL.md 中的路径）
LINK_PATH="$HOME/.openclaw/skills/zhihu"
if [ ! -e "$LINK_PATH" ]; then
    mkdir -p "$(dirname "$LINK_PATH")"
    ln -s "$SKILL_DIR" "$LINK_PATH"
    echo "创建软链接: $LINK_PATH -> $SKILL_DIR"
elif [ -L "$LINK_PATH" ] && [ "$(readlink "$LINK_PATH")" != "$SKILL_DIR" ]; then
    rm "$LINK_PATH"
    ln -s "$SKILL_DIR" "$LINK_PATH"
    echo "更新软链接: $LINK_PATH -> $SKILL_DIR"
fi

# Check python3
if ! command -v python3 &>/dev/null; then
    echo "错误: 需要 python3，请先安装"
    exit 1
fi

echo "python3: $(python3 --version)"

# Test the client
echo ""
echo "测试 zhihu_client.py ..."
python3 "$SCRIPT_DIR/zhihu_client.py" 2>&1 | head -3

echo ""
echo "初始化完成! 可以开始使用知乎搜索了。"
echo "示例: python3 $SCRIPT_DIR/zhihu_client.py search \"AI\""
