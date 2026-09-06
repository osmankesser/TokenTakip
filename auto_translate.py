"""Kısa metin otomatik çevirisi — Google Translate gtx + disk önbellek.

ponytail: resmi API anahtarı yok; translate.googleapis.com/?client=gtx.
Ağ yoksa veya hata olursa orijinal metin döner. Kod satırlarını olduğu gibi bırakır.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from platform_util import app_cache_dir

_CACHE_NAME = "translate_gtx.json"
_UA = "TokenTracker/1"
_MAX_Q = 1800
_CODEISH = re.compile(
    r"^(git |npm |pip |cargo |go |cd |python |npx |#\{|\"mcpServers\"|https?://)",
    re.I,
)


FORCE_OFFLINE = False


def _cache_path() -> Path:
    return app_cache_dir() / _CACHE_NAME


def _load_cache() -> dict[str, str]:
    path = _cache_path()
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except (OSError, ValueError, json.JSONDecodeError):
        return {}


def _save_cache(cache: dict[str, str]) -> None:
    path = _cache_path()
    try:
        # ponytail: dosya büyürse LRU yok; ~4k giriş tavanı
        if len(cache) > 4000:
            keys = list(cache.keys())[len(cache) - 3000 :]
            cache = {k: cache[k] for k in keys}
        path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


_MEM: dict[str, str] = {}
_DISK: dict[str, str] | None = None


def _disk() -> dict[str, str]:
    global _DISK
    if _DISK is None:
        _DISK = _load_cache()
    return _DISK


def normalize_lang(lang: str) -> str:
    code = (lang or "en").replace("_", "-").split("-")[0].lower()
    return code or "en"


def _key(text: str, dest: str, src: str) -> str:
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]
    return f"{src}|{dest}|{h}"


def _looks_code_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if _CODEISH.match(s):
        return True
    if s.startswith("{") or s.startswith("}") or s.startswith('"'):
        return True
    return False


def _split_preserve_code(text: str) -> list[tuple[bool, str]]:
    """(is_code, chunk) — kod satırları çevrilmez."""
    parts: list[tuple[bool, str]] = []
    buf: list[str] = []
    code_mode: bool | None = None
    for line in text.splitlines(keepends=True):
        is_code = _looks_code_line(line.rstrip("\n"))
        if code_mode is None:
            code_mode = is_code
        if is_code != code_mode:
            parts.append((code_mode, "".join(buf)))
            buf = [line]
            code_mode = is_code
        else:
            buf.append(line)
    if buf:
        parts.append((bool(code_mode), "".join(buf)))
    return parts or [(False, text)]


def _gtx_request(text: str, dest: str, src: str) -> str:
    q = text[:_MAX_Q]
    params = urllib.parse.urlencode(
        {"client": "gtx", "sl": src, "tl": dest, "dt": "t", "q": q}
    )
    url = f"https://translate.googleapis.com/translate_a/single?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": _UA}, method="GET")
    with urllib.request.urlopen(req, timeout=8) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    data = json.loads(raw)
    # [[[translated, original, ...], ...], ...]
    chunks = data[0] if isinstance(data, list) and data else None
    if not isinstance(chunks, list):
        return text
    out: list[str] = []
    for row in chunks:
        if isinstance(row, list) and row and isinstance(row[0], str):
            out.append(row[0])
    return "".join(out).strip() or text


def translate(text: str, dest_lang: str, *, src: str = "auto") -> str:
    """Metni hedef dile çevir. Başarısızsa orijinali döndür."""
    text = (text or "").strip()
    if not text:
        return text
    if FORCE_OFFLINE:
        return text
    dest = normalize_lang(dest_lang)
    if dest == "en" and src == "en":
        return text
    # Tek satırlık saf kod
    if "\n" not in text and _looks_code_line(text):
        return text

    cache_key = _key(text, dest, src)
    if cache_key in _MEM:
        return _MEM[cache_key]
    disk = _disk()
    if cache_key in disk:
        _MEM[cache_key] = disk[cache_key]
        return disk[cache_key]

    try:
        if "\n" in text:
            pieces: list[str] = []
            for is_code, chunk in _split_preserve_code(text):
                if not chunk.strip():
                    pieces.append(chunk)
                elif is_code:
                    pieces.append(chunk)
                else:
                    pieces.append(_gtx_request(chunk, dest, src))
            result = "".join(pieces).strip() or text
        else:
            result = _gtx_request(text, dest, src)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError, json.JSONDecodeError):
        return text
    except Exception:
        return text

    _MEM[cache_key] = result
    disk[cache_key] = result
    _save_cache(disk)
    return result


def translate_many(texts: list[str], dest_lang: str, *, src: str = "auto") -> list[str]:
    return [translate(t, dest_lang, src=src) for t in texts]


def clear_memory_cache() -> None:
    _MEM.clear()
