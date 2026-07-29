#!/usr/bin/env bash
# VisiDot - 一键启动（Ubuntu / Linux）
# 用法：chmod +x start.sh && ./start.sh
# 关闭：在此终端按 Ctrl+C，服务会优雅停止并释放端口。

# 切到脚本所在目录，保证从项目根提供静态文件
cd "$(dirname "$(readlink -f "$0")")" || exit 1

# 找可用的 python3
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "[错误] 未找到 Python，请先安装 Python 3："
    echo "        sudo apt install python3"
    exit 1
fi

exec "$PY" serve.py
