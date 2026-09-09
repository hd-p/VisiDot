#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
色卡识别工具 - 本地静态服务器 / 一键启动
- 从本脚本所在目录提供静态文件（index.html / data.js / 色卡图片）
- 启动后自动打开浏览器
- 关闭时（Ctrl+C 或关闭窗口）优雅回收资源：停止服务、释放 socket、关闭端口
"""

import atexit
import contextlib
import http.server
import os
import signal
import socket
import socketserver
import sys
import threading
import webbrowser

HOST = "127.0.0.1"
PREFERRED_PORT = 8770
ROOT = os.path.dirname(os.path.abspath(__file__))


def find_free_port(host, preferred):
    """优先用 preferred 端口；被占用则让系统分配一个空闲端口。"""
    for candidate in (preferred, 0):
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((host, candidate))
                return s.getsockname()[1]
            except OSError:
                continue
    raise RuntimeError("无法找到可用端口")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        # 禁用缓存，保证修改 data.js / 图片后刷新即生效
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        # 精简日志：只在出错时打印
        status = args[1] if len(args) > 1 else ""
        if str(status).startswith(("4", "5")):
            sys.stderr.write("[%s] %s\n" % (self.address_string(), fmt % args))


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True       # 关闭时不等待挂起的请求线程
    allow_reuse_address = True  # 立即释放端口，避免 TIME_WAIT 占用


def main():
    port = find_free_port(HOST, PREFERRED_PORT)
    url = "http://%s:%d/index.html" % (HOST, port)

    httpd = Server((HOST, port), Handler)

    stopping = threading.Event()

    def shutdown(*_):
        if stopping.is_set():
            return
        stopping.set()
        print("\n正在关闭服务，回收资源…")
        # shutdown() 停止 serve_forever 循环；server_close() 释放监听 socket / 端口
        threading.Thread(target=httpd.shutdown, daemon=True).start()

    # 覆盖各种关闭信号：Ctrl+C、终止、Windows 关闭窗口(CTRL_BREAK)
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(ValueError, AttributeError, OSError):
            signal.signal(sig, shutdown)
    if hasattr(signal, "SIGBREAK"):
        with contextlib.suppress(ValueError, AttributeError, OSError):
            signal.signal(signal.SIGBREAK, shutdown)

    # 进程无论如何退出都确保 socket 被关闭
    atexit.register(httpd.server_close)

    print("=" * 48)
    print("  色卡识别工具已启动")
    print("  地址: %s" % url)
    print("  关闭: 在此窗口按 Ctrl+C，或直接关闭窗口")
    print("=" * 48)

    with contextlib.suppress(Exception):
        webbrowser.open(url)

    try:
        httpd.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        shutdown()
    finally:
        httpd.server_close()  # 显式释放端口
        print("已关闭，端口已释放。")


if __name__ == "__main__":
    main()
