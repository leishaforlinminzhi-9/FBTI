#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs


ROOT = Path(__file__).resolve().parent
INDEX_HTML = ROOT / "index.html"
DATA_DIR = ROOT / "data"
LOGINS_NDJSON = DATA_DIR / "logins.ndjson"


def _json_bytes(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "FBTI/0.1"

    def _set_headers(self, status: int, *, content_type: str, extra: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        # Basic CORS to allow sharing through other origins if needed.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        if extra:
            for k, v in extra.items():
                self.send_header(k, v)
        self.end_headers()

    def _read_json_body(self, max_bytes: int = 64 * 1024) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        if length > max_bytes:
            raise ValueError("body_too_large")
        raw = self.rfile.read(length)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def do_OPTIONS(self) -> None:
        self._set_headers(HTTPStatus.NO_CONTENT, content_type="text/plain; charset=utf-8")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            if not INDEX_HTML.exists():
                self._set_headers(HTTPStatus.NOT_FOUND, content_type="text/plain; charset=utf-8")
                self.wfile.write(b"index.html not found\n")
                return
            self._set_headers(HTTPStatus.OK, content_type="text/html; charset=utf-8")
            self.wfile.write(INDEX_HTML.read_bytes())
            return

        if path == "/questions.json":
            fp = ROOT / "questions.json"
            if not fp.exists():
                self._set_headers(HTTPStatus.NOT_FOUND, content_type="text/plain; charset=utf-8")
                self.wfile.write(b"questions.json not found\n")
                return
            self._set_headers(HTTPStatus.OK, content_type="application/json; charset=utf-8")
            self.wfile.write(fp.read_bytes())
            return

        if path == "/results.json":
            fp = ROOT / "results.json"
            if not fp.exists():
                self._set_headers(HTTPStatus.NOT_FOUND, content_type="text/plain; charset=utf-8")
                self.wfile.write(b"results.json not found\n")
                return
            self._set_headers(HTTPStatus.OK, content_type="application/json; charset=utf-8")
            self.wfile.write(fp.read_bytes())
            return

        if path == "/api/health":
            self._set_headers(HTTPStatus.OK, content_type="application/json; charset=utf-8")
            self.wfile.write(_json_bytes({"ok": True, "ts": int(time.time())}))
            return

        if path == "/api/logins":
            # Optional: ?limit=100
            qs = parse_qs(parsed.query or "")
            limit = None
            if "limit" in qs:
                try:
                    limit = max(1, min(2000, int(qs["limit"][0])))
                except Exception:
                    limit = None

            DATA_DIR.mkdir(parents=True, exist_ok=True)
            if not LOGINS_NDJSON.exists():
                self._set_headers(HTTPStatus.OK, content_type="application/json; charset=utf-8")
                self.wfile.write(_json_bytes({"items": []}))
                return

            lines = LOGINS_NDJSON.read_text("utf-8").splitlines()
            if limit is not None:
                lines = lines[-limit:]
            items = []
            for ln in lines:
                try:
                    items.append(json.loads(ln))
                except Exception:
                    continue
            self._set_headers(HTTPStatus.OK, content_type="application/json; charset=utf-8")
            self.wfile.write(_json_bytes({"items": items}))
            return

        self._set_headers(HTTPStatus.NOT_FOUND, content_type="text/plain; charset=utf-8")
        self.wfile.write(b"Not found\n")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/login":
            try:
                payload = self._read_json_body()
            except ValueError:
                self._set_headers(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, content_type="application/json; charset=utf-8")
                self.wfile.write(_json_bytes({"ok": False, "error": "body_too_large"}))
                return
            except Exception:
                self._set_headers(HTTPStatus.BAD_REQUEST, content_type="application/json; charset=utf-8")
                self.wfile.write(_json_bytes({"ok": False, "error": "invalid_json"}))
                return

            nick = str(payload.get("nickname", "")).strip()
            team = str(payload.get("team", "")).strip()
            code = str(payload.get("code", "")).strip()  # optional: may be empty before quiz

            if not nick:
                self._set_headers(HTTPStatus.BAD_REQUEST, content_type="application/json; charset=utf-8")
                self.wfile.write(_json_bytes({"ok": False, "error": "nickname_required"}))
                return

            item = {
                "ts": int(time.time()),
                "nickname": nick[:32],
                "team": team[:64],
                "code": code[:8],
                "ip": self.client_address[0],
                "ua": self.headers.get("User-Agent", "")[:200],
                "path": self.headers.get("Referer", "")[:200],
            }

            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(LOGINS_NDJSON, "a", encoding="utf-8") as f:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

            self._set_headers(HTTPStatus.OK, content_type="application/json; charset=utf-8")
            self.wfile.write(_json_bytes({"ok": True}))
            return

        self._set_headers(HTTPStatus.NOT_FOUND, content_type="application/json; charset=utf-8")
        self.wfile.write(_json_bytes({"ok": False, "error": "not_found"}))

    def log_message(self, fmt: str, *args) -> None:
        # Keep logs concise
        msg = fmt % args
        print(f"[{time.strftime('%H:%M:%S')}] {self.client_address[0]} {self.command} {self.path} - {msg}")


def main() -> None:
    host = os.environ.get("FBTI_HOST", "0.0.0.0")
    port = int(os.environ.get("FBTI_PORT", "8787"))
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"FBTI server running on http://{host}:{port}")
    print("Endpoints: / , /api/login (POST), /api/logins (GET), /api/health (GET)")
    httpd.serve_forever()


if __name__ == "__main__":
    main()

