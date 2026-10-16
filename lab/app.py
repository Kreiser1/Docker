"""Учебный сервис. Только стандартная библиотека; не production-сервер."""
import json
import os
import socket
import sqlite3
import uuid
from threading import Lock
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROLE = os.getenv("ROLE", "web")
PORT = int(os.getenv("PORT", "8000"))
BIND = os.getenv("BIND", "0.0.0.0")
API_URL = os.getenv("API_URL", "http://api:8000")
DATA = Path(os.getenv("DATA_DIR", "/data"))
KINDS = {"screen": "Не работает экран", "battery": "Не заряжается", "software": "Не запускается программа"}
INSTANCE = socket.gethostname()
COUNTS = {200: 0, 201: 0, 400: 0, 404: 0, 503: 0}
COUNT_LOCK = Lock()


def emit(event, **fields):
    print(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "role": ROLE,
                      "event": event, **fields}, ensure_ascii=False), flush=True)


def connect():
    db = sqlite3.connect(DATA / "requests.sqlite", timeout=5)
    db.row_factory = sqlite3.Row
    return db


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        emit("http", method=self.command, path=self.path, detail=format % args)

    def send(self, status, payload, content_type="application/json; charset=utf-8"):
        if self.path not in {"/metrics", "/health"}:
            with COUNT_LOCK:
                COUNTS[status] = COUNTS.get(status, 0) + 1
        body = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/metrics":
            with COUNT_LOCK:
                counts = dict(COUNTS)
            lines = ["# HELP devops_http_requests_total Business HTTP responses since process start.",
                     "# TYPE devops_http_requests_total counter"]
            lines.extend(f'devops_http_requests_total{{role="{ROLE}",status="{status}"}} {count}'
                         for status, count in sorted(counts.items()))
            return self.send(200, ("\n".join(lines) + "\n").encode(), "text/plain; version=0.0.4")
        if self.path == "/api/banner":
            if ROLE == "web":
                return self.proxy()
            path = DATA / "banner.txt"
            return self.send(200, {"message": path.read_text(encoding="utf-8").strip() if path.exists() else "Workshop is open"})
        if self.path == "/health":
            return self.send(200, {"process": "running", "role": ROLE})
        if ROLE == "web":
            if self.path in ("/", "/index.html"):
                return self.send(200, Path(__file__).with_name("index.html").read_bytes(), "text/html; charset=utf-8")
            if self.path == "/api/requests":
                return self.proxy()
        elif self.path == "/api/requests":
            with connect() as db:
                rows = [dict(row) for row in db.execute("SELECT id, kind, created FROM requests ORDER BY id DESC LIMIT 20")]
                total = db.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
            return self.send(200, {"requests": rows, "total": total, "instance": INSTANCE})
        self.send(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/api/requests":
            return self.send(404, {"error": "not_found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 2048:
                return self.send(400, {"error": "invalid_body"})
            body = self.rfile.read(length)
            data = json.loads(body)
            kind, key = data.get("kind"), data.get("key")
            if kind not in KINDS or not isinstance(key, str) or not 1 <= len(key) <= 80:
                return self.send(400, {"error": "invalid_request"})
        except (ValueError, AttributeError, TypeError):
            return self.send(400, {"error": "invalid_json"})
        if ROLE == "web":
            return self.proxy(body)
        with connect() as db:
            db.execute("INSERT OR IGNORE INTO requests (kind, created, request_key) VALUES (?, ?, ?)",
                       (kind, datetime.now(timezone.utc).isoformat(), key))
            row = dict(db.execute("SELECT id, kind, created FROM requests WHERE request_key=?", (key,)).fetchone())
        emit("request_accepted", request_id=row["id"])
        self.send(201, {"request": row, "instance": INSTANCE})

    def proxy(self, body=None):
        request_id = str(uuid.uuid4())[:8]
        request = Request(API_URL + self.path, data=body,
                          headers={"Content-Type": "application/json"}, method=self.command)
        try:
            with urlopen(request, timeout=2) as response:
                self.send(response.status, response.read())
        except HTTPError as error:
            self.send(error.code, error.read())
        except (URLError, TimeoutError, ConnectionError, OSError) as error:
            emit("upstream_unavailable", request_id=request_id, target=API_URL, error=str(error))
            self.send(503, {"error": "upstream_unavailable", "request_id": request_id})


if __name__ == "__main__":
    if ROLE not in {"api", "web"}:
        raise SystemExit("ROLE must be api or web")
    if ROLE == "api":
        DATA.mkdir(parents=True, exist_ok=True)
        with connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, created TEXT NOT NULL, request_key TEXT NOT NULL UNIQUE)")
    emit("started", port=PORT, instance=INSTANCE)
    ThreadingHTTPServer((BIND, PORT), Handler).serve_forever()
