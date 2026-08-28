"""Bir kerelik: flagcdn PNG -> assets/flags/. Uygulama calisirken ag yok."""
from __future__ import annotations

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "flags"
# overlay.FLAG_ISO + dogrudan dil kodlari
CODES = (
    "tr", "gb", "es", "pt", "sa", "ir", "in", "bd", "pk", "cn", "jp", "kr",
    "vn", "my", "sv", "cz", "sk", "hr", "rs", "az", "ke",
)
PNG = b"\x89PNG\r\n\x1a\n"


def _fetch(cc: str) -> bytes:
    url = f"https://flagcdn.com/w80/{cc}.png"
    req = urllib.request.Request(url, headers={"User-Agent": "TokenTracker/1"})
    data = urllib.request.urlopen(req, timeout=12).read()
    if len(data) < 200 or not data.startswith(PNG):
        raise RuntimeError(f"{cc}: gecersiz png ({len(data)} byte)")
    return data


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ok = 0
    for cc in CODES:
        path = OUT / f"{cc}.png"
        data = _fetch(cc)
        path.write_bytes(data)
        print(cc, len(data))
        ok += 1
    print(f"{ok} bayrak -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
