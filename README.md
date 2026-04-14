# FBTI（Frisbee Behavior Type Indicator）

一个移动端优先的飞盘人格测试 SPA（模仿 MBTI 的玩法）。前端技术栈为 **HTML + Tailwind（CDN）+ Alpine.js**。

本仓库提供两种使用方式：

- **纯静态部署**：适合 GitHub Pages（不需要后端）
- **可选后端**（`server.py`）：用于本地/服务器托管静态资源，并记录访问日志到本地文件（可选）

## 在线访问（GitHub Pages）

如果仓库启用了 GitHub Pages，你可以直接打开 Pages 地址访问（无需安装依赖）。

## 本地运行

由于浏览器安全策略，直接双击打开 `index.html`（`file://`）时可能无法读取 `questions.json` / `results.json`。
建议用下面任一方式启动本地静态服务：

### 方式 A：使用本仓库自带 Python 服务（推荐）

```bash
python3 server.py
```

然后访问 `http://127.0.0.1:8787/`。

### 方式 B：任意静态服务器

例如：

```bash
python3 -m http.server 8787
```

或：

```bash
npx serve .
```

### 离线整合版（可选）

如果你希望单文件打开即可运行，可以使用 `standalone.html`（题库与结果映射已内置）。

## 目录结构

- `index.html`：主版本（读取 `questions.json` / `results.json`）
- `standalone.html`：离线整合版（内置题库和结果映射）
- `questions.json`：题库数据
- `results.json`：结果映射数据（含 `partnerSuggestions` / `logic`）
- `image/fbti/`：16 种人格对应的结果图片（文件名为 `HSVW.png` 这类代码）
- `server.py`：可选 Python 服务（静态托管 + 记录日志）
- `data/logins.ndjson`：日志文件（NDJSON，一行一个 JSON）

## 在其他设备上访问（同一 Wi‑Fi / 局域网）

1. 确保手机/电脑与运行服务的机器在同一局域网（同一 Wi‑Fi）。
2. 在服务所在机器上找到局域网 IP：

```bash
ip -4 addr | sed -n 's/.*inet \\([0-9.]*\\)\\/.*/\\1/p'
```

3. 在其他设备浏览器打开：

- `http://<你的局域网IP>:8787/`

示例：`http://192.168.1.23:8787/`

### 常见问题

- **其他设备打不开**
  - 确认服务监听的是 `0.0.0.0`（`server.py` 默认如此）
  - 确认防火墙放行端口 `8787`
  - 确认路由器/热点没有开启“客户端隔离（AP isolation）”
- **端口被占用**
  - 使用其它端口：`FBTI_PORT=8790 python3 server.py`
- **题库加载失败**
  - 请通过 `http://` 访问（不要 `file://` 打开 `index.html`）
  - 或直接打开 `standalone.html`

## 可选后端：日志与 API

当使用 `server.py` 启动时，会写入：

- `data/logins.ndjson`

可用 API：

- 健康检查：`GET /api/health`
- 记录日志：`POST /api/login`
- 查询日志：`GET /api/logins?limit=100`

```bash
curl -sS "http://127.0.0.1:8787/api/logins?limit=20"
```

## 公网分享（可选）

如果你希望不在同一局域网的人也能访问：

- **推荐**：把服务跑在有公网 IP 的服务器上，用 Nginx/Caddy 反代到 `127.0.0.1:8787` 并配置 HTTPS
- **临时**：使用内网穿透（frp / cloudflared tunnel / ngrok 等）

注意：`server.py` 目前**没有鉴权**，仅适合演示或小范围分享。

