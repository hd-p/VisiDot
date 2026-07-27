#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
色卡识别工具 - RK3588 无头静态服务器
- 提供本脚本所在目录的静态文件（quiz.html / index.html / data.js / *-areal.webp）
- 根路径 / 映射到测试工具 quiz.html；复核台经 /index.html 访问
- 监听 0.0.0.0，便于局域网内其它设备访问
- 不打开浏览器（板子无桌面）
- 收到 SIGINT/SIGTERM 时优雅关闭并释放端口
"""

import atexit
import contextlib
import http.server
import os
import signal
import socketserver
import sys
import threading

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8770"))
ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def send_head(self):
        # 根路径提供测试工具（quiz.html）而非复核台；复核台仍可经 /index.html 访问
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path == "/":
            self.path = "/quiz.html"
        return super().send_head()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        status = args[1] if len(args) > 1 else ""
        if str(status).startswith(("4", "5")):
            sys.stderr.write("[%s] %s\n" % (self.address_string(), fmt % args))


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    httpd = Server((HOST, PORT), Handler)
    stopping = threading.Event()

    def shutdown(*_):
        if stopping.is_set():
            return
        stopping.set()
        threading.Thread(target=httpd.shutdown, daemon=True).start()

    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(ValueError, AttributeError, OSError):
            signal.signal(sig, shutdown)
    atexit.register(httpd.server_close)

    print("serving %s on %s:%d" % (ROOT, HOST, PORT), flush=True)
    try:
        httpd.serve_forever(poll_interval=0.5)
    finally:
        httpd.server_close()
        print("stopped, port released", flush=True)


if __name__ == "__main__":
    main()
