"""Telefonda aynı cam ekran: durum + koç özeti. Stdlib HTTP."""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable

Holder: Callable[[], dict] = lambda: {}
_httpd: ThreadingHTTPServer | None = None
PORT = 8765


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/api"):
            body = json.dumps(Holder(), ensure_ascii=False).encode("utf-8")
            self._send(body, "application/json")
            return
        self._send(_PAGE.encode("utf-8"), "text/html; charset=utf-8")


    def _send(self, body: bytes, ctype: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


def start(get_state: Callable[[], dict]) -> str:
    global _httpd, Holder
    Holder = get_state
    if _httpd:
        return f"http://127.0.0.1:{PORT}/"
    _httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    threading.Thread(target=_httpd.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{PORT}/"


_PAGE = """<!doctype html>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pulse</title>
<style>
body{margin:0;font-family:system-ui;background:linear-gradient(#0b1220,#1e1b4b);color:#f8fafc;min-height:100vh}
.phone{max-width:420px;margin:12px auto;padding:18px;border-radius:36px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.28);backdrop-filter:blur(18px)}
h1{font-size:20px;margin:0 0 8px}
.card{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);border-radius:16px;padding:12px;margin:10px 0}
.muted{color:#cbd5e1;font-size:13px;white-space:pre-wrap}
.big{display:flex;gap:8px}
.big button{flex:1;min-height:48px;border-radius:14px;border:1px solid rgba(255,255,255,.35);background:rgba(255,255,255,.12);color:#fff}
</style>
<div class="phone">
<h1>Pulse</h1>
<p class="muted" id="sum">yükleniyor</p>
<div class="big">
<button onclick="location.reload()">Durum</button>
<button onclick="alert('Durdur masadaki pencereden')">Durdur</button>
</div>
<div class="card" id="body"></div>
</div>
<script>
fetch('/api').then(r=>r.json()).then(d=>{
  document.getElementById('sum').textContent=d.summary||'';
  document.getElementById('body').innerHTML='<div class=muted>'+ (d.html||'') +'</div>';
});
</script>
"""
