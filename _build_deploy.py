"""Test + PyInstaller + kök TokenTracker.exe deploy."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = ROOT / ".venv" / "Scripts" / "python.exe"
PI = ROOT / ".venv" / "Scripts" / "pyinstaller.exe"


def _stop_running() -> None:
    if sys.platform != "win32":
        return
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-Process TokenTracker -ErrorAction SilentlyContinue | Stop-Process -Force",
        ],
        check=False,
    )


def _launch_exe() -> None:
    exe = ROOT / "TokenTracker.exe"
    if not exe.is_file():
        return
    if sys.platform == "win32":
        os.startfile(exe)
    else:
        subprocess.Popen([str(exe)], cwd=ROOT, start_new_session=True)


def main() -> int:
    if not PY.is_file() or not PI.is_file():
        print(".venv yok; once: python -m venv .venv && pip install -r requirements-release.txt", file=sys.stderr)
        return 1
    _stop_running()
    print("--- purge ---")
    rc = subprocess.run([str(PY), "_purge_legacy.py"], cwd=ROOT).returncode
    if rc:
        return rc
    assets = ROOT / "assets" / "flags"
    if not (assets / "tr.png").is_file():
        print("--- flag assets ---")
        rc = subprocess.run([str(PY), "_fetch_flag_assets.py"], cwd=ROOT).returncode
        if rc:
            print("flag assets failed", file=sys.stderr)
            return rc
    steps = (
        ([str(PY), "-m", "unittest", "test_privacy", "test_license", "test_buttons", "-q"], "test"),
        (
            [str(PI), "-y", "--distpath", "release_out", "--workpath", "build_out", "TokenTracker_onedir.spec"],
            "pyinstaller",
        ),
        ([str(PY), "_deploy_root.py"], "deploy"),
        ([str(PY), "_pack_release.py"], "release"),
    )
    for cmd, label in steps:
        print(f"--- {label} ---")
        rc = subprocess.run(cmd, cwd=ROOT).returncode
        if rc:
            print(f"{label} failed ({rc})", file=sys.stderr)
            return rc
    print("TokenTracker.exe guncel:", ROOT / "TokenTracker.exe")
    print("Yayin ZIP:", ROOT / "release" / f"TokenTracker-{__import__('version').VERSION}-win64.zip")
    _launch_exe()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
