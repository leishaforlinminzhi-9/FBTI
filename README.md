# FBTI（飞盘人格测试）服务运行指南

这是一个移动端优先的单页应用（`index.html`），并配套一个轻量后端（`server.py`）用于：

- 托管页面与 JSON 数据（`questions.json` / `results.json`）
- 记录“登录/进入”信息到本地文件（`data/logins.ndjson`）

## 目录结构

- `index.html`：前端 SPA
- `questions.json`：题库数据
- `results.json`：结果映射数据（含 `partnerSuggestions` / `logic`）
- `server.py`：Python 后端（静态托管 + 记录登录）
- `data/logins.ndjson`：登录记录（NDJSON，一行一个 JSON）

## 环境要求

- Python 3（推荐 3.10+；本项目在 Python 3.13 可用）

## 启动服务（本机）

在项目目录执行：

```bash
cd /data/minzhi/agent/fbti
python3 server.py
```

默认监听：`0.0.0.0:8787`

打开浏览器访问：

- 本机：`http://127.0.0.1:8787/`

### 自定义端口/监听地址（可选）

```bash
# 改端口
FBTI_PORT=8787 python3 server.py

# 只监听本机（不允许局域网访问）
FBTI_HOST=127.0.0.1 python3 server.py
```

## 其他设备如何访问（同一 Wi-Fi/局域网）

1. 确保你的手机/其他电脑 **和服务器在同一个局域网**（同一 Wi-Fi / 同一网段）。
2. 找到服务器的局域网 IP：

```bash
ip -4 addr | sed -n 's/.*inet \\([0-9.]*\\)\\/.*/\\1/p'
```

一般会看到类似 `192.168.x.x` 或 `10.x.x.x` 的地址，选那个是你正在用的网卡对应的 IP。

3. 在手机浏览器输入：

- `http://<你的局域网IP>:8787/`

示例：

- `http://192.168.1.23:8787/`

### 常见问题排查

- **能访问 `127.0.0.1`，但手机访问不了**
  - 确认服务监听的是 `0.0.0.0`（默认就是）
  - 确认服务器防火墙放行端口 `8787`
  - 确认路由器/热点没有开启“客户端隔离（AP isolation）”
- **端口被占用**
  - 换端口：`FBTI_PORT=8790 python3 server.py`
- **不要用双击打开 `index.html`**
  - `file://` 模式下浏览器会限制 `fetch` 读取 `questions.json/results.json`，必须通过 `server.py` 访问。

## 查看登录记录

### 文件方式

登录记录会写入：

- `data/logins.ndjson`

每行一个 JSON，字段包含 `ts`、`nickname`、`team`、`ip`、`ua` 等。

### API 方式

- 健康检查：`GET /api/health`
- 记录登录：`POST /api/login`
- 查看登录：`GET /api/logins?limit=100`

例子：

```bash
curl -sS "http://127.0.0.1:8787/api/logins?limit=20"
```

## 公网转发给大家（可选）

如果你希望不在同一局域网的人也能访问，常见做法：

### 方案 A：反向代理/已有服务器（推荐）

把 `server.py` 跑在一台有公网 IP 的机器上，然后在 Nginx/Caddy 上做反代到 `127.0.0.1:8787`，对外提供 `https://...`。

### 方案 B：内网穿透（临时分享）

如果你没有公网服务器，可以用内网穿透工具把 `8787` 暴露出去（例如 frp / cloudflared tunnel / ngrok 等）。

注意：这会把你的服务暴露到公网；本服务目前**没有鉴权**，只适合临时演示或小范围分享。

