"""Kaynak kaydedilince overlay yeniden açılır. Qt sınıfları süreç içinde yama kabul etmez."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = ROOT / ".venv" / "Scripts" / "python.exe"
CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


def _files() -> list[Path]:
    return sorted(p for p in ROOT.glob("*.py") if p.name != "live.py")


def _stamp() -> tuple[tuple[str, float], ...]:
    out = []
    for path in _files():
        try:
            out.append((path.name, path.stat().st_mtime))
        except OSError:
            pass
    return tuple(out)


def _kill_stray() -> None:
    if sys.platform != "win32":
        return
    me = os.getpid()
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Process | "
            f"Where-Object {{ $_.CommandLine -like '*overlay.py*' -and $_.ProcessId -ne {me} }} | "
            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }",
        ],
        creationflags=CREATE_NO_WINDOW,
    )


def _start() -> subprocess.Popen:
    py = str(PY if PY.exists() else sys.executable)
    return subprocess.Popen([py, str(ROOT / "overlay.py")], cwd=str(ROOT))


def main() -> int:
    if "--check" in sys.argv:
        assert _files() and _stamp()
        print("live-ok")
        return 0
    _kill_stray()
    prev = _stamp()
    proc = _start()
    print("canli: overlay acik, py kaydi yeniler", flush=True)
    try:
        while True:
            time.sleep(0.4)
            now = _stamp()
            if now == prev:
                continue
            time.sleep(0.3)
            prev = _stamp()
            proc.terminate()
            try:
                proc.wait(timeout=4)
            except subprocess.TimeoutExpired:
                proc.kill()
            proc = _start()
            print("canli: yeniden acildi", flush=True)
    except KeyboardInterrupt:
        proc.terminate()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
