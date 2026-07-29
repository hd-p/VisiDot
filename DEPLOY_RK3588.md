# 色卡识别工具 — RK3588 部署说明

## 一、部署结果

已部署到 RK3588 开发板并验证通过（HTTP 200）。

| 项目 | 值 |
|---|---|
| 访问地址（局域网） | **http://192.168.31.135:8770/index.html** |
| 设备 | Khadas RK3588 (aarch64, Linux 6.1.118) |
| 运行环境 | Python 3.12.3（标准库，无第三方依赖） |
| 远程目录 | `/home/khadas/color-test` |
| 监听 | `0.0.0.0:8770`（局域网内任意设备可访问） |
| 已上传 | `index.html`、`data.js`、`rk_serve.py` + 112 张 `-areal.png`（v5×65 + v6×47），共 ~258MB |

> 注意：`192.168.31.135` 是**局域网内网地址**，只有与开发板处于同一网络（同一路由器/WiFi）的设备能访问。外网访问需另配内网穿透（如 Cloudflare Tunnel）或端口映射。

---

## 二、访问方式

同一局域网下，任意设备浏览器打开：

```
http://192.168.31.135:8770/index.html
```

手机、平板、电脑均可。

---

## 三、服务管理（在开发板上操作）

SSH 登录开发板：

```bash
ssh khadas@192.168.31.135
```

### 查看服务状态

```bash
# 是否在运行
pgrep -af rk_serve.py

# 端口是否监听
ss -ltnp | grep 8770

# 查看日志
cat /home/khadas/color-test/serve.log
```

### 启动服务

```bash
cd /home/khadas/color-test
PORT=8770 setsid nohup python3 rk_serve.py > serve.log 2>&1 &
```

`setsid` + `nohup` 让服务脱离终端常驻，SSH 断开后仍继续运行。

### 停止服务

```bash
pkill -f rk_serve.py
```

服务收到信号后会优雅关闭并释放端口（内置 SIGINT/SIGTERM 处理）。

### 重启服务

```bash
pkill -f rk_serve.py ; sleep 1
cd /home/khadas/color-test
PORT=8770 setsid nohup python3 rk_serve.py > serve.log 2>&1 &
```

### 更换端口

把上面命令里的 `PORT=8770` 改成别的端口即可，例如 `PORT=8080`。

---

## 四、开机自启（可选）

若希望开发板重启后自动拉起服务，用 systemd：

```bash
sudo tee /etc/systemd/system/color-test.service > /dev/null <<'EOF'
[Unit]
Description=Color Plate Viewer
After=network.target

[Service]
Type=simple
User=khadas
WorkingDirectory=/home/khadas/color-test
Environment=PORT=8770
ExecStart=/usr/bin/python3 /home/khadas/color-test/rk_serve.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now color-test
```

管理：

```bash
sudo systemctl status color-test    # 状态
sudo systemctl restart color-test   # 重启
sudo systemctl stop color-test      # 停止
```

启用 systemd 后，不要再用 `nohup` 手动启动，避免端口冲突。

---

## 五、更新内容（本机 → 开发板）

在本机 `output/` 目录下重新运行部署脚本即可增量上传（已存在且大小一致的文件自动跳过）：

```bash
python deploy_rk.py
```

脚本会：从 `.env` 读取连接信息 → SFTP 上传变更文件 → 重启远端服务。

> 若已改用 systemd 自启，`deploy_rk.py` 里的 `nohup` 重启方式会与 systemd 冲突，建议部署后改为手动执行 `sudo systemctl restart color-test`。

---

## 六、相关文件

| 文件 | 作用 |
|---|---|
| `rk_serve.py` | 开发板上的无头静态服务器（监听 0.0.0.0，无浏览器弹出，优雅关闭） |
| `deploy_rk.py` | 本机部署脚本（SFTP 上传 + 远端重启，可续传） |
| `index.html` | 单页应用 |
| `data.js` | 112 张色卡的页码-关键信息数据 |
| `.env` | 开发板连接信息（IP / 用户 / 密码），**勿提交到公开仓库** |

---

## 七、故障排查

| 现象 | 排查 |
|---|---|
| 打不开页面 | 确认访问设备与开发板在**同一局域网**；`ping 192.168.31.135` |
| 端口不通 | 开发板上 `ss -ltnp \| grep 8770` 看服务是否在监听 |
| 服务没起来 | `cat /home/khadas/color-test/serve.log` 看报错 |
| 图片加载慢 | 单张 areal 图较大（最大 ~4MB），首次加载需等待；局域网通常可接受 |
| SSH 登录失败 | `.env` 为 CRLF 换行，值末尾带 `\r`，脚本已 strip 处理；手动登录用真实密码 |
