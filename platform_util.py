"""Windows / macOS / Linux yolları ve başlangıç kaydı."""

from __future__ import annotations

import os
import struct
import sys
import time
from pathlib import Path

IS_WINDOWS = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

RUN_NAME = "TokenTracker"
_RUN_LEGACY = ("PulseTokenTakip", "TokenTakip")
STARTUP_ARG = "--tray"
_LAUNCH_AGENT = "com.tokentracker.app.plist"
_AUTOSTART_NAME = "TokenTracker.desktop"


def platform_ok() -> tuple[bool, str]:
    if struct.calcsize("P") * 8 < 64:
        return False, "Token Tracker requires a 64-bit system."
    if IS_WINDOWS:
        if sys.getwindowsversion().major < 10:
            return False, "Token Tracker requires Windows 10 or newer."
    elif not (IS_MAC or IS_LINUX):
        return False, f"Unsupported platform: {sys.platform}"
    return True, ""


def show_platform_error(message: str) -> None:
    if IS_WINDOWS:
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, message, "Token Tracker", 0x10)
            return
        except Exception:
            pass
    print(message, file=sys.stderr)


def home(*parts: str) -> Path:
    return Path.home().joinpath(*parts)


def roaming(*parts: str) -> Path:
    if IS_WINDOWS:
        return Path(os.environ.get("APPDATA", "")).joinpath(*parts)
    if IS_MAC:
        return home("Library", "Application Support", *parts)
    config = os.environ.get("XDG_CONFIG_HOME")
    base = Path(config) if config else home(".config")
    return base.joinpath(*parts)


def local(*parts: str) -> Path:
    if IS_WINDOWS:
        return Path(os.environ.get("LOCALAPPDATA", "")).joinpath(*parts)
    if IS_MAC:
        return home("Library", "Application Support", *parts)
    data = os.environ.get("XDG_DATA_HOME")
    base = Path(data) if data else home(".local", "share")
    return base.joinpath(*parts)


def app_cache_dir(*parts: str) -> Path:
    root = local("TokenTracker", "cache", *parts)
    root.mkdir(parents=True, exist_ok=True)
    return root


def program_roots() -> list[Path]:
    if IS_WINDOWS:
        roots = [
            local("Programs"),
            roaming("Microsoft", "Windows", "Start Menu", "Programs"),
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
        ]
    elif IS_MAC:
        roots = [Path("/Applications"), home("Applications")]
    else:
        roots = [
            Path("/usr/bin"),
            Path("/usr/local/bin"),
            home(".local", "bin"),
            Path("/opt"),
            Path("/snap/bin"),
        ]
    return [path for path in roots if path.exists()]


def gh_cli_args() -> list[list[str]]:
    paths: list[list[str]] = [["gh", "auth", "token"]]
    if IS_WINDOWS:
        paths.extend(
            [
                [str(local("Programs", "GitHub CLI", "gh.exe")), "auth", "token"],
                [r"C:\Program Files\GitHub CLI\gh.exe", "auth", "token"],
            ]
        )
    return paths


def subprocess_flags() -> int:
    if IS_WINDOWS:
        import subprocess

        return subprocess.CREATE_NO_WINDOW
    return 0


def startup_registered() -> bool:
    if IS_WINDOWS:
        return _windows_run_name() is not None
    if IS_MAC:
        return _mac_agent_path().is_file()
    if IS_LINUX:
        return _linux_autostart_path().is_file()
    return False


def startup_exec() -> str:
    if getattr(sys, "frozen", False):
        return f"{sys.executable} {STARTUP_ARG}"
    root = Path(__file__).resolve().parent
    py = Path(sys.executable).with_name("pythonw.exe")
    if not py.is_file():
        py = Path(sys.executable)
    return f"{py} {root / 'overlay.py'} {STARTUP_ARG}"


def startup_cmd() -> str:
    parts = startup_exec().split(" ", 1)
    if len(parts) == 1:
        return f'"{parts[0]}"'
    return f'"{parts[0]}" {parts[1]}'


def _startup_approved_blob(enabled: bool) -> bytes:
    if enabled:
        return b"\x02" + b"\x00" * 11
    stamp = int((time.time() + 11644473600) * 10_000_000)
    return struct.pack("<B3xQ", 0x03, stamp)


def _windows_run_name() -> str | None:
    import winreg

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
    except OSError:
        return None
    for name in (RUN_NAME, *_RUN_LEGACY):
        try:
            winreg.QueryValueEx(key, name)
            return name
        except OSError:
            continue
    return None


def _windows_approved_enabled(name: str) -> bool:
    import winreg

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
        )
        raw, _ = winreg.QueryValueEx(key, name)
    except OSError:
        return True
    return not (isinstance(raw, (bytes, bytearray)) and raw and raw[0] == 0x03)


def _mac_agent_path() -> Path:
    return home("Library", "LaunchAgents", _LAUNCH_AGENT)


def _linux_autostart_path() -> Path:
    config = os.environ.get("XDG_CONFIG_HOME")
    base = Path(config) if config else home(".config")
    return base / "autostart" / _AUTOSTART_NAME


def startup_on() -> bool:
    if IS_WINDOWS:
        name = _windows_run_name()
        return name is not None and _windows_approved_enabled(name)
    if IS_MAC:
        return _mac_agent_path().is_file()
    if IS_LINUX:
        path = _linux_autostart_path()
        if not path.is_file():
            return False
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return False
        return "X-GNOME-Autostart-enabled=false" not in text.replace(" ", "")
    return False


def set_startup(on: bool) -> None:
    if IS_WINDOWS:
        _set_startup_windows(on)
    elif IS_MAC:
        _set_startup_mac(on)
    elif IS_LINUX:
        _set_startup_linux(on)


def _set_startup_windows(on: bool) -> None:
    import winreg

    run_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    approved_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
    run = winreg.CreateKey(winreg.HKEY_CURRENT_USER, run_key)
    approved = winreg.CreateKey(winreg.HKEY_CURRENT_USER, approved_key)
    if on:
        winreg.SetValueEx(run, RUN_NAME, 0, winreg.REG_SZ, startup_cmd())
        winreg.SetValueEx(approved, RUN_NAME, 0, winreg.REG_BINARY, _startup_approved_blob(True))
        for legacy in _RUN_LEGACY:
            for key in (run, approved):
                try:
                    winreg.DeleteValue(key, legacy)
                except FileNotFoundError:
                    pass
        return
    if _windows_run_name() is None:
        return
    winreg.SetValueEx(run, RUN_NAME, 0, winreg.REG_SZ, startup_cmd())
    for legacy in _RUN_LEGACY:
        for key in (run, approved):
            try:
                winreg.DeleteValue(key, legacy)
            except FileNotFoundError:
                pass
        try:
            winreg.DeleteValue(run, legacy)
        except FileNotFoundError:
            pass
    winreg.SetValueEx(approved, RUN_NAME, 0, winreg.REG_BINARY, _startup_approved_blob(False))


def _set_startup_mac(on: bool) -> None:
    path = _mac_agent_path()
    if on:
        path.parent.mkdir(parents=True, exist_ok=True)
        if getattr(sys, "frozen", False):
            args = [sys.executable, STARTUP_ARG]
        else:
            root = Path(__file__).resolve().parent
            args = [sys.executable, str(root / "overlay.py"), STARTUP_ARG]
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
            '<plist version="1.0"><dict>',
            "  <key>Label</key><string>com.tokentracker.app</string>",
            "  <key>ProgramArguments</key><array>",
        ]
        for arg in args:
            lines.append(f"    <string>{arg}</string>")
        lines.extend(
            [
                "  </array>",
                "  <key>RunAtLoad</key><true/>",
                "</dict></plist>",
            ]
        )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    if path.is_file():
        path.unlink(missing_ok=True)


def _set_startup_linux(on: bool) -> None:
    path = _linux_autostart_path()
    if on:
        path.parent.mkdir(parents=True, exist_ok=True)
        cmd = startup_exec()
        path.write_text(
            "\n".join(
                [
                    "[Desktop Entry]",
                    "Type=Application",
                    "Name=Token Tracker",
                    f"Exec={cmd}",
                    "Terminal=false",
                    "X-GNOME-Autostart-enabled=true",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return
    if path.is_file():
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    ok, err = platform_ok()
    assert ok, err
    assert roaming("Cursor").name == "Cursor"
    assert startup_on() == startup_on()
    print("platform_util ok", sys.platform)
