#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把色卡识别工具部署到 RK3588（通过 SFTP）。
- 从 .env 读取 RK3588_IP / RK3588_USER / RK3588_PASSWORD（自动去除 CRLF）
- 只上传 app 实际引用的文件：index.html、data.js、rk_serve.py、data.js 中引用的 *-areal.png
- 可续传：远端已存在且大小一致的文件跳过
- 上传完成后在板子上以 nohup 后台启动 rk_serve.py，并打印访问地址
"""

import os
import posixpath
import re
import stat
import sys
import time

import paramiko

HERE = os.path.dirname(os.path.abspath(__file__))
REMOTE_DIR = "/home/khadas/color-test"
PORT = 8770


def _shquote(s):
    """把整段脚本安全地包成单引号参数，供 `bash -c` 执行。"""
    return "'" + s.replace("'", "'\\''") + "'"


def load_env():
    env = {}
    with open(os.path.join(HERE, ".env"), "rb") as f:
        for line in f.read().decode("utf-8", "replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def referenced_files():
    """从 data.js 解析出引用的图片相对路径。"""
    with open(os.path.join(HERE, "data.js"), "r", encoding="utf-8") as f:
        txt = f.read()
    files = re.findall(r'"file":\s*"([^"]+)"', txt)
    return sorted(set(files))


def ensure_remote_dirs(sftp, path):
    parts = path.strip("/").split("/")
    cur = ""
    for p in parts:
        cur += "/" + p
        try:
            sftp.stat(cur)
        except IOError:
            sftp.mkdir(cur)


def remote_size(sftp, path):
    try:
        return sftp.stat(path).st_size
    except IOError:
        return None


def upload(sftp, local, remote):
    lsize = os.path.getsize(local)
    if remote_size(sftp, remote) == lsize:
        return "skip"
    rdir = posixpath.dirname(remote)
    ensure_remote_dirs(sftp, rdir)
    sftp.put(local, remote)
    return "sent"


def main():
    env = load_env()
    host = env["RK3588_IP"]
    user = env["RK3588_USER"]
    pw = env["RK3588_PASSWORD"]

    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(host, username=user, password=pw, timeout=15)
    sftp = cli.open_sftp()

    ensure_remote_dirs(sftp, REMOTE_DIR)

    core = ["index.html", "data.js", "rk_serve.py"]
    imgs = referenced_files()
    all_files = core + imgs

    sent = skipped = 0
    t0 = time.time()
    for i, rel in enumerate(all_files, 1):
        local = os.path.join(HERE, rel.replace("/", os.sep))
        remote = posixpath.join(REMOTE_DIR, rel)
        if not os.path.exists(local):
            print("  MISSING local: %s" % rel, flush=True)
            continue
        res = upload(sftp, local, remote)
        if res == "sent":
            sent += 1
        else:
            skipped += 1
        if i % 10 == 0 or res == "sent":
            print("  [%d/%d] %s %s" % (i, len(all_files), res, rel), flush=True)

    print("upload done: %d sent, %d skipped, %.1fs"
          % (sent, skipped, time.time() - t0), flush=True)

    # 重启服务：先杀掉旧实例，再 nohup 后台启动
    # 用换行拼接：后台启动 `... &` 后面不能紧跟 `;`，否则 bash 报语法错误。
    # setsid 让服务脱离 SSH 会话常驻。
    script = "\n".join([
        "pkill -f rk_serve.py || true",
        "sleep 1",
        "cd %s && PORT=%d setsid nohup python3 rk_serve.py > serve.log 2>&1 &" % (REMOTE_DIR, PORT),
        "sleep 2",
        "cat %s/serve.log" % REMOTE_DIR,
    ])
    stdin, stdout, stderr = cli.exec_command("bash -c %s" % _shquote(script))
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    print("--- server log ---", flush=True)
    print(out.strip() or err.strip(), flush=True)

    print("\n访问地址（局域网）: http://%s:%d/index.html" % (host, PORT), flush=True)

    sftp.close()
    cli.close()


if __name__ == "__main__":
    main()
