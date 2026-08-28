"""Cursor ve Codex kalan kullanımını yerel oturumdan okur."""

from __future__ import annotations

import base64
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


CURSOR_CLIENT_ID = "KbZUR41cY7W6zRSdpSUJ7I7mLYBKOCmB"
CURSOR_API = "https://api2.cursor.sh"
CODEX_USAGE_URLS = (
    "https://chatgpt.com/backend-api/codex/usage",
    "https://chatgpt.com/backend-api/wham/usage",
)
ALLOWED_API_HOSTS = frozenset(
    {
        "api2.cursor.sh",
        "chatgpt.com",
        "api.anthropic.com",
        "cloudcode-pa.googleapis.com",
        "api.github.com",
    }
)
_QUERY_SECRET_KEYS = frozenset(
    {"token", "access_token", "refresh_token", "authorization", "client_secret", "password"}
)


@dataclass
class Meter:
    label: str
    remaining_percent: float | None = None
    used_percent: float | None = None
    remaining_text: str = ""
    reset_text: str = ""
    detail: str = ""
    ok: bool = True
    error: str = ""


@dataclass
class ProviderUsage:
    name: str
    plan: str = ""
    meters: list[Meter] = field(default_factory=list)
    error: str = ""


@dataclass
class UsageSnapshot:
    checked_at: str
    providers: list[ProviderUsage] = field(default_factory=list)
    cursor: list[Meter] = field(default_factory=list)
    codex: list[Meter] = field(default_factory=list)
    cursor_plan: str = ""
    cursor_error: str = ""
    codex_plan: str = ""
    codex_error: str = ""


def fetch_snapshot(*, allow_quota: bool = False) -> UsageSnapshot:
    now = datetime.now().strftime("%H:%M:%S")
    if not allow_quota:
        return UsageSnapshot(checked_at=now)
    found = [(name, load) for name, detect, load in _PROVIDER_LOADERS if detect()]
    first = [job for job in found if job[0] in ("CURSOR", "CODEX", "CHATGPT")]
    rest = [job for job in found if job not in first]
    providers = _run_jobs(first, 10)
    providers += _run_jobs(rest, 6)
    extra = _scan_unknown_installs({name for name, _ in found})
    providers += _run_jobs(extra, 5)
    snap = UsageSnapshot(checked_at=now, providers=providers)
    for item in providers:
        if item.name == "CURSOR":
            snap.cursor, snap.cursor_plan, snap.cursor_error = item.meters, item.plan, item.error
        elif item.name == "CODEX":
            snap.codex, snap.codex_plan, snap.codex_error = item.meters, item.plan, item.error
    return snap


def _safe_err(_exc: BaseException | None = None) -> str:
    return "error.generic"


def _run_jobs(jobs: list, timeout: int) -> list[ProviderUsage]:
    providers: list[ProviderUsage] = []

    def run(name: str, load):
        try:
            return load()
        except Exception as exc:
            code = getattr(exc, "safe_code", None)
            return ProviderUsage(name=name, error=code if isinstance(code, str) else _safe_err(exc))

    if not jobs:
        return providers
    with ThreadPoolExecutor(max_workers=min(8, len(jobs))) as pool:
        futures = [pool.submit(run, name, load) for name, load in jobs]
        for future, (name, _) in zip(futures, jobs):
            try:
                providers.append(future.result(timeout=timeout))
            except FuturesTimeout:
                providers.append(ProviderUsage(name=name, error="error.timeout"))
    return providers


def _sort_key(item: ProviderUsage) -> tuple:
    leftover = 101.0
    for meter in item.meters:
        if meter.remaining_percent is not None:
            leftover = min(leftover, meter.remaining_percent)
    has_quota = leftover < 101.0
    return (0 if has_quota else 1, leftover, item.name)


def _plan_key(raw: str) -> str:
    if not raw:
        return ""
    if raw.startswith("plan."):
        return raw
    low = raw.strip().lower()
    known = {
        "individual": "plan.individual",
        "free": "plan.free",
        "pro": "plan.pro",
        "plus": "plan.plus",
        "team": "plan.team",
        "business": "plan.business",
        "enterprise": "plan.enterprise",
    }
    return known.get(low, raw)


def remaining_of(used: float | None) -> float | None:
    if used is None:
        return None
    return max(0.0, min(100.0, 100.0 - float(used)))


def _cursor_meters() -> tuple[str, list[Meter]]:
    token = _cursor_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Connect-Protocol-Version": "1",
    }
    usage = _json_post(f"{CURSOR_API}/aiserver.v1.DashboardService/GetCurrentPeriodUsage", b"{}", headers)
    plan = _json_post(f"{CURSOR_API}/aiserver.v1.DashboardService/GetPlanInfo", b"{}", headers)
    info = plan.get("planInfo") or {}
    plan_name = str(info.get("planName") or "").strip()
    price = str(info.get("price") or "").strip()
    title = " · ".join(part for part in (plan_name, price) if part)

    plan_usage = usage.get("planUsage") or {}
    meters: list[Meter] = []

    total_used = _finite(plan_usage.get("totalPercentUsed"))
    if total_used is None:
        limit = _cents(plan_usage.get("limit"))
        remaining = _cents(plan_usage.get("remaining"))
        if limit and remaining is not None:
            total_used = max(0.0, min(100.0, (limit - remaining) / limit * 100.0))
    meters.append(
        Meter(
            label="meter.total",
            used_percent=total_used,
            remaining_percent=remaining_of(total_used),
            remaining_text=_percent_left(remaining_of(total_used)),
            reset_text=_cycle_reset(usage.get("billingCycleEnd") or info.get("billingCycleEnd")),
            detail=_spend_detail(plan_usage),
        )
    )

    auto_used = _finite(plan_usage.get("autoPercentUsed"))
    if auto_used is not None:
        meters.append(
            Meter(
                label="meter.auto",
                used_percent=auto_used,
                remaining_percent=remaining_of(auto_used),
                remaining_text=_percent_left(remaining_of(auto_used)),
            )
        )

    api_used = _finite(plan_usage.get("apiPercentUsed"))
    if api_used is not None:
        meters.append(
            Meter(
                label="meter.api",
                used_percent=api_used,
                remaining_percent=remaining_of(api_used),
                remaining_text=_percent_left(remaining_of(api_used)),
            )
        )

    spend = usage.get("spendLimitUsage") or {}
    individual_limit = _cents(spend.get("individualLimit"))
    pooled_limit = _cents(spend.get("pooledLimit"))
    if individual_limit:
        remaining = _cents(spend.get("individualRemaining"))
        used = _cents(spend.get("individualUsed"))
        pct_used = None if not individual_limit else (used or 0) / individual_limit * 100.0
        meters.append(
            Meter(
                label="meter.ondemand",
                used_percent=pct_used,
                remaining_percent=remaining_of(pct_used),
                remaining_text=_money_left(remaining),
                detail=f"fmt.limit|{_usd(individual_limit)}",
            )
        )
    elif pooled_limit:
        remaining = _cents(spend.get("pooledRemaining"))
        used = _cents(spend.get("pooledUsed"))
        pct_used = None if not pooled_limit else (used or 0) / pooled_limit * 100.0
        meters.append(
            Meter(
                label="meter.pool",
                used_percent=pct_used,
                remaining_percent=remaining_of(pct_used),
                remaining_text=_money_left(remaining),
                detail=f"fmt.limit|{_usd(pooled_limit)}",
            )
        )
    return title, meters


def _codex_meters() -> tuple[str, list[Meter]]:
    try:
        return _codex_from_http()
    except Exception:
        cli = _codex_from_cli()
        if cli:
            return cli
        raise


def _codex_from_cli() -> tuple[str, list[Meter]] | None:
    try:
        proc = subprocess.run(
            ["codex", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=4,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    limits = payload.get("rateLimits") or {}
    if not limits:
        return None
    return _meters_from_codex_limits(limits)


def _codex_from_http() -> tuple[str, list[Meter]]:
    auth = _codex_auth()
    token = auth.get("access_token") or ""
    account_id = auth.get("account_id") or ""
    if not token:
        raise _SafeError("error.session")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if account_id:
        headers["ChatGPT-Account-Id"] = str(account_id)
    last_error = _SafeError("error.http")
    for url in CODEX_USAGE_URLS:
        try:
            payload = _json_get(url, headers)
            return _meters_from_codex_http(payload)
        except _SafeError as exc:
            last_error = exc
        except Exception:
            last_error = _SafeError("error.generic")
    raise last_error


def _meters_from_codex_limits(limits: dict[str, Any]) -> tuple[str, list[Meter]]:
    plan = str(limits.get("planType") or limits.get("plan") or "").strip()
    meters: list[Meter] = []
    primary = limits.get("primary") or {}
    secondary = limits.get("secondary") or {}
    if primary:
        meters.append(_window_meter(_window_label(primary, "meter.5h"), primary))
    if secondary:
        meters.append(_window_meter(_window_label(secondary, "meter.weekly"), secondary))
    credits = limits.get("credits") or {}
    balance = str(credits.get("balance") or "").strip()
    if credits and not credits.get("unlimited") and balance not in ("", "0"):
        meters.append(
            Meter(
                label="meter.credit",
                remaining_text=balance,
                detail="detail.credit_balance",
            )
        )
    return plan.title() if plan else "Codex", meters


def _meters_from_codex_http(payload: dict[str, Any]) -> tuple[str, list[Meter]]:
    plan = str(
        payload.get("plan_type")
        or payload.get("planType")
        or ((payload.get("rate_limit") or {}).get("plan_type"))
        or ""
    ).strip()
    meters: list[Meter] = []

    def add_window(fallback: str, block: Any) -> None:
        if not isinstance(block, dict):
            return
        used = _finite(block.get("used_percent") if "used_percent" in block else block.get("usedPercent"))
        meters.append(
            Meter(
                label=_window_label(block, fallback),
                used_percent=used,
                remaining_percent=remaining_of(used),
                remaining_text=_percent_left(remaining_of(used)),
                reset_text=_unix_reset(block.get("reset_at") or block.get("resetsAt")),
            )
        )

    rate = payload.get("rate_limit") or payload.get("rateLimit") or payload
    add_window("meter.5h", rate.get("primary_window") or rate.get("primary"))
    add_window("meter.weekly", rate.get("secondary_window") or rate.get("secondary"))

    if not meters:
        for key, label in (
            ("five_hour", "meter.5h"),
            ("weekly", "meter.weekly"),
            ("seven_day", "meter.weekly"),
        ):
            add_window(label, payload.get(key))

    credits = payload.get("credits") or {}
    if isinstance(credits, dict):
        balance = str(credits.get("balance") or "").strip()
        if balance not in ("", "0", "None"):
            meters.append(Meter(label="meter.credit", remaining_text=balance, detail="detail.credit_balance"))
    return plan.title() if plan else "Codex", meters


def _window_label(block: dict[str, Any], fallback: str) -> str:
    mins = _finite(block.get("windowDurationMins") or block.get("window_duration_mins"))
    if mins is None:
        return fallback
    if mins <= 360:
        return "meter.5h"
    if mins <= 24 * 60 + 30:
        return "meter.daily"
    return "meter.weekly"


def _window_meter(label: str, block: dict[str, Any]) -> Meter:
    used = _finite(block.get("usedPercent") if "usedPercent" in block else block.get("used_percent"))
    extra = ""
    return Meter(
        label=label,
        used_percent=used,
        remaining_percent=remaining_of(used),
        remaining_text=_percent_left(remaining_of(used)),
        reset_text=_unix_reset(block.get("resetsAt") or block.get("reset_at")),
        detail=extra,
    )


def _cursor_access_token() -> str:
    values = _cursor_auth_values()
    access = values.get("cursorAuth/accessToken") or ""
    refresh = values.get("cursorAuth/refreshToken") or ""
    if access and not _jwt_expired(access):
        return access
    if not refresh:
        if access:
            return access
        raise _SafeError("error.session")
    refreshed = _refresh_cursor_token(refresh)
    return refreshed or access


def _cursor_auth_values() -> dict[str, str]:
    db_path = Path(os.environ.get("APPDATA", "")) / "Cursor" / "User" / "globalStorage" / "state.vscdb"
    if not db_path.exists():
        raise _SafeError("error.session")
    keys = (
        "cursorAuth/accessToken",
        "cursorAuth/refreshToken",
        "cursorAuth/cachedEmail",
        "cursorAuth/stripeMembershipType",
    )
    try:
        rows = _read_sqlite_kv(db_path, keys)
    except sqlite3.Error:
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "state.vscdb"
            copy.write_bytes(db_path.read_bytes())
            rows = _read_sqlite_kv(copy, keys)
    return rows


def _read_sqlite_kv(db_path: Path, keys: tuple[str, ...]) -> dict[str, str]:
    uri = db_path.as_uri() + "?mode=ro"
    con = sqlite3.connect(uri, uri=True, timeout=3)
    try:
        placeholders = ",".join("?" for _ in keys)
        cur = con.execute(f"SELECT key, value FROM ItemTable WHERE key IN ({placeholders})", keys)
        return {str(k): str(v) for k, v in cur.fetchall() if v}
    finally:
        con.close()


def _refresh_cursor_token(refresh_token: str) -> str:
    body = json.dumps(
        {
            "grant_type": "refresh_token",
            "client_id": CURSOR_CLIENT_ID,
            "refresh_token": refresh_token,
        }
    ).encode("utf-8")
    payload = _json_post(
        f"{CURSOR_API}/oauth/token",
        body,
        {"Content-Type": "application/json"},
    )
    token = str(payload.get("access_token") or "")
    if payload.get("shouldLogout") or not token:
        raise _SafeError("error.session")
    return token


def _codex_auth() -> dict[str, str]:
    path = Path.home() / ".codex" / "auth.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    tokens = data.get("tokens") if isinstance(data.get("tokens"), dict) else data
    return {
        "access_token": str(tokens.get("access_token") or data.get("access_token") or ""),
        "account_id": str(tokens.get("account_id") or data.get("account_id") or ""),
    }


def _jwt_expired(token: str, skew: int = 60) -> bool:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload.encode("ascii")))
        exp = int(data.get("exp") or 0)
        return exp <= int(time.time()) + skew
    except Exception:
        return False


class _SafeError(RuntimeError):
    def __init__(self, code: str = "error.generic"):
        self.safe_code = code
        super().__init__(code)


def _assert_api_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise _SafeError("error.network")
    if parsed.username is not None or parsed.password is not None:
        raise _SafeError("error.network")
    host = parsed.hostname
    if host is None or host not in ALLOWED_API_HOSTS:
        raise _SafeError("error.network")
    query = parse_qs(parsed.query, keep_blank_values=True)
    if _QUERY_SECRET_KEYS & {k.lower() for k in query}:
        raise _SafeError("error.network")


class _ApiRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        _assert_api_url(newurl)
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req is None:
            return None
        # Cross-host: never forward Authorization / tokens
        if urlparse(req.full_url).hostname != urlparse(newurl).hostname:
            for key in ("Authorization", "authorization"):
                if key in new_req.headers:
                    del new_req.headers[key]
            raise _SafeError("error.network")
        return new_req


_API_OPENER = urllib.request.build_opener(_ApiRedirectHandler)


def _json_post(url: str, body: bytes, headers: dict[str, str]) -> dict[str, Any]:
    _assert_api_url(url)
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    return _read_json(req)


def _json_get(url: str, headers: dict[str, str]) -> dict[str, Any]:
    _assert_api_url(url)
    req = urllib.request.Request(url, headers=headers, method="GET")
    return _read_json(req)


def _read_json(req: urllib.request.Request) -> dict[str, Any]:
    try:
        with _API_OPENER.open(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
    except _SafeError:
        raise
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise _SafeError("error.auth") from None
        if exc.code == 404:
            raise _SafeError("error.not_found") from None
        raise _SafeError("error.http") from None
    except urllib.error.URLError:
        raise _SafeError("error.network") from None
    except OSError:
        raise _SafeError("error.network") from None
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise _SafeError("error.http") from None
    if not isinstance(data, dict):
        raise _SafeError("error.http")
    return data


def _finite(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number or number in (float("inf"), float("-inf")):
        return None
    return number


def _cents(value: Any) -> float | None:
    number = _finite(value)
    if number is None:
        return None
    return number / 100.0


def _usd(amount: float | None) -> str:
    if amount is None:
        return "—"
    return f"${amount:,.2f}"


def _percent_left(remaining: float | None) -> str:
    if remaining is None:
        return "—"
    n = remaining if remaining >= 10 else round(remaining, 1)
    return f"left|{n}"


def _money_left(amount: float | None) -> str:
    if amount is None:
        return "—"
    return f"fmt.money_left|{_usd(amount)}"


def _spend_detail(plan_usage: dict[str, Any]) -> str:
    included = _cents(plan_usage.get("includedSpend"))
    limit = _cents(plan_usage.get("limit"))
    remaining = _cents(plan_usage.get("remaining"))
    if included is not None and limit:
        return f"fmt.spend_pair|{_usd(included)}|{_usd(limit)}"
    if remaining is not None:
        return f"fmt.balance|{_usd(remaining)}"
    return ""


def _cycle_reset(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        stamp = int(str(value))
    except ValueError:
        return ""
    if stamp > 10_000_000_000:
        stamp //= 1000
    dt = datetime.fromtimestamp(stamp)
    return f"reset.at|{dt.strftime('%d.%m %H:%M')}"


def _unix_reset(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        stamp = int(float(value))
    except (TypeError, ValueError):
        return ""
    if stamp > 10_000_000_000:
        stamp //= 1000
    dt = datetime.fromtimestamp(stamp)
    delta = int(stamp - time.time())
    if delta <= 0:
        return "reset.resetting"
    hours, rem = divmod(delta, 3600)
    minutes = rem // 60
    if hours >= 48:
        days = hours // 24
        return f"reset.in_days|{days}|{hours % 24}|{dt.strftime('%d.%m %H:%M')}"
    if hours:
        return f"reset.in_hours|{hours}|{minutes}|{dt.strftime('%H:%M')}"
    return f"reset.in_mins|{minutes}|{dt.strftime('%H:%M')}"


def _home(*parts: str) -> Path:
    return Path.home().joinpath(*parts)


def _roaming(*parts: str) -> Path:
    return Path(os.environ.get("APPDATA", "")).joinpath(*parts)


def _local(*parts: str) -> Path:
    return Path(os.environ.get("LOCALAPPDATA", "")).joinpath(*parts)


def _any_exists(*paths: Path) -> bool:
    return any(path.exists() for path in paths)


def _cmd_exists(name: str) -> bool:
    return shutil.which(name) is not None


def _run_text(args: list[str]) -> str:
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    proc = subprocess.run(args, capture_output=True, text=True, timeout=12, creationflags=flags)
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip()


def _github_token() -> str:
    for value in (os.environ.get("GITHUB_TOKEN"), os.environ.get("GH_TOKEN")):
        if value:
            return value.strip()
    token = _github_token_from_hosts()
    if token:
        return token
    paths = [
        ["gh", "auth", "token"],
        [str(_local("Programs", "GitHub CLI", "gh.exe")), "auth", "token"],
        [r"C:\Program Files\GitHub CLI\gh.exe", "auth", "token"],
    ]
    for args in paths:
        if args[0] != "gh" and not Path(args[0]).exists():
            continue
        text = _run_text(args)
        if text:
            return text.splitlines()[0].strip()
    return ""


def _github_token_from_hosts() -> str:
    for path in (_home(".config", "gh", "hosts.yml"), _roaming("GitHub CLI", "hosts.yml")):
        if not path.exists():
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped.startswith("oauth_token:"):
                    return stripped.split(":", 1)[1].strip().strip("'\"")
        except OSError:
            continue
    return ""


def _unlimited(name: str, detail: str) -> ProviderUsage:
    return ProviderUsage(
        name=name,
        plan="plan.local",
        meters=[Meter(label="meter.quota", remaining_percent=100, remaining_text="meter.unlimited", detail=detail)],
    )


def _installed(name: str, detail: str) -> ProviderUsage:
    return ProviderUsage(
        name=name,
        meters=[Meter(label="meter.status", remaining_text="meter.no_quota", detail=detail)],
    )


def _folder_names() -> list[str]:
    names: list[str] = []
    folders = (
        _local("Programs"),
        _roaming("Microsoft", "Windows", "Start Menu", "Programs"),
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
    )
    for folder in folders:
        try:
            if folder.exists():
                names.extend(item.name.lower() for item in folder.iterdir())
        except OSError:
            continue
    return names


_SCAN_MAP = (
    ("OLLAMA", ("ollama",), lambda: _unlimited("OLLAMA", "detail.local_no_internet")),
    ("LM STUDIO", ("lm studio", "lmstudio"), lambda: _unlimited("LM STUDIO", "detail.local_no_internet")),
    ("TABNINE", ("tabnine",), lambda: _installed("TABNINE", "detail.tabnine")),
    ("AMAZON Q", ("amazon q", "amazonq", "codewhisperer"), lambda: _installed("AMAZON Q", "detail.amazon_q")),
    ("JETBRAINS AI", ("jetbrains",), lambda: _installed("JETBRAINS AI", "detail.jetbrains")),
    ("AIDER", ("aider",), lambda: _installed("AIDER", "detail.aider")),
    ("GROQ", ("groq",), lambda: _installed("GROQ", "detail.groq")),
    ("QWEN", ("qwen",), lambda: _installed("QWEN", "detail.qwen")),
    ("CLINE", ("cline",), lambda: _installed("CLINE", "detail.cline")),
)


def _scan_unknown_installs(already: set[str]) -> list[tuple[str, Any]]:
    names = _folder_names()
    blob = " ".join(names)
    extra = []
    for title, keys, loader in _SCAN_MAP:
        if title in already:
            continue
        if any(key in blob or (" " not in key and _cmd_exists(key)) for key in keys):
            extra.append((title, loader))
    return extra


def github_token() -> str:
    return _github_token()


def _load_cursor() -> ProviderUsage:
    plan, meters = _cursor_meters()
    return ProviderUsage(name="CURSOR", plan=plan, meters=meters)


def _detect_cursor() -> bool:
    return (_roaming("Cursor", "User", "globalStorage", "state.vscdb").exists() or _cmd_exists("cursor"))


def _load_codex() -> ProviderUsage:
    plan, meters = _codex_meters()
    return ProviderUsage(name="CODEX", plan=plan, meters=meters)


def _detect_codex() -> bool:
    return _home(".codex", "auth.json").exists() or _cmd_exists("codex")


def _detect_claude() -> bool:
    return _any_exists(
        _home(".claude", ".credentials.json"),
        _home(".claude"),
        _local("AnthropicClaude"),
        _local("Programs", "Claude"),
        _roaming("Claude"),
    ) or _cmd_exists("claude")


def _load_claude() -> ProviderUsage:
    cred = _home(".claude", ".credentials.json")
    if not cred.exists():
        return _installed("CLAUDE", "detail.no_session_file")
    data = json.loads(cred.read_text(encoding="utf-8"))
    oauth = data.get("claudeAiOauth") if isinstance(data.get("claudeAiOauth"), dict) else data
    token = str(oauth.get("accessToken") or oauth.get("access_token") or "")
    if not token:
        return _installed("CLAUDE", "detail.no_token")
    payload = _json_get(
        "https://api.anthropic.com/api/oauth/usage",
        {"Authorization": f"Bearer {token}", "anthropic-beta": "oauth-2025-04-20"},
    )
    meters = []
    for key, label in (
        ("five_hour", "meter.5h"),
        ("seven_day", "meter.weekly"),
        ("seven_day_sonnet", "Sonnet"),
        ("seven_day_opus", "Opus"),
    ):
        window = payload.get(key)
        if not isinstance(window, dict):
            continue
        used = _finite(window.get("utilization"))
        meters.append(
            Meter(
                label=label,
                used_percent=used,
                remaining_percent=remaining_of(used),
                remaining_text=_percent_left(remaining_of(used)),
                reset_text=_iso_reset(window.get("resets_at")),
            )
        )
    tier = str(oauth.get("rateLimitTier") or "")
    return ProviderUsage(name="CLAUDE", plan=tier.title(), meters=meters or [Meter(label="meter.status", remaining_text="meter.no_quota")])


def _detect_gemini() -> bool:
    return _home(".gemini", "oauth_creds.json").exists() or _cmd_exists("gemini")


def _load_gemini() -> ProviderUsage:
    cred_path = _home(".gemini", "oauth_creds.json")
    if not cred_path.exists():
        return _installed("GEMINI", "detail.no_session_file")
    creds = json.loads(cred_path.read_text(encoding="utf-8"))
    token = str(creds.get("access_token") or "")
    if not token:
        return _installed("GEMINI", "detail.no_token")
    body = json.dumps({}).encode("utf-8")
    payload = _json_post(
        "https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota",
        body,
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    meters = []
    for bucket in payload.get("userQuotaBuckets") or []:
        if not isinstance(bucket, dict):
            continue
        remaining = _finite(bucket.get("remainingFraction"))
        used = None if remaining is None else (1 - remaining) * 100
        model = str(bucket.get("modelId") or "meter.quota")
        meters.append(
            Meter(
                label=model,
                used_percent=used,
                remaining_percent=remaining_of(used),
                remaining_text=_percent_left(remaining_of(used)),
                reset_text=_iso_reset(bucket.get("resetTime")),
            )
        )
    return ProviderUsage(name="GEMINI", meters=meters or [Meter(label="meter.status", remaining_text="meter.no_quota")])


def _detect_copilot() -> bool:
    return _any_exists(
        _roaming("Code", "User", "globalStorage", "github.copilot-chat"),
        _roaming("Cursor", "User", "globalStorage", "github.copilot-chat"),
        _home(".copilot"),
    ) or _cmd_exists("gh") or _cmd_exists("copilot")


def _copilot_snapshots(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("quota_snapshots") or payload.get("quotaSnapshots") or {}
    if not isinstance(raw, dict):
        return {}
    norm: dict[str, Any] = {}
    for key, snap in raw.items():
        if not isinstance(snap, dict):
            continue
        slot = "premium_interactions" if key in ("premiumInteractions", "premium_interactions") else str(key)
        norm.setdefault(slot, snap)
    return norm


def _copilot_meter(label: str, snap: dict[str, Any], reset: str) -> Meter | None:
    """Skip unpurchased buckets (entitlement 0 → percent 0 looks critical but isn't)."""
    if snap.get("unlimited"):
        return Meter(
            label=label,
            remaining_percent=100,
            remaining_text="meter.unlimited",
            reset_text=reset,
        )
    ent = _finite(snap.get("entitlement"))
    # No allotment bought / assigned — not a quota to alarm on
    if ent is not None and ent <= 0:
        return None
    left = _finite(snap.get("percent_remaining"))
    if left is None:
        rem = _finite(snap.get("remaining") if snap.get("remaining") is not None else snap.get("quota_remaining"))
        if ent and rem is not None:
            left = max(0.0, min(100.0, rem / ent * 100.0))
        else:
            return None
    return Meter(
        label=label,
        used_percent=100 - left,
        remaining_percent=left,
        remaining_text=_percent_left(left),
        reset_text=reset,
    )


def _load_copilot() -> ProviderUsage:
    token = _github_token()
    if not token:
        return _installed("COPILOT", "detail.copilot_no_auth")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Editor-Version": "vscode/1.96.2",
        "User-Agent": "GitHubCopilotChat/0.26.7",
        "X-GitHub-Api-Version": "2025-04-01",
    }
    try:
        payload = _json_get("https://api.github.com/copilot_internal/user", headers)
    except _SafeError as exc:
        if exc.safe_code == "error.auth":
            return _installed("COPILOT", "detail.copilot_auth_invalid")
        if exc.safe_code == "error.not_found":
            return _installed("COPILOT", "detail.copilot_no_sub")
        raise
    reset = _iso_reset(payload.get("quota_reset_date_utc") or payload.get("quota_reset_date"))
    meters = []
    for key, label in (
        ("premium_interactions", "Premium"),
        ("chat", "Chat"),
        ("completions", "meter.completions"),
    ):
        snap = _copilot_snapshots(payload).get(key) or {}
        if not isinstance(snap, dict) or not snap:
            continue
        meter = _copilot_meter(label, snap, reset)
        if meter:
            meters.append(meter)
    plan = _plan_key(str(payload.get("copilot_plan") or payload.get("copilotPlan") or ""))
    if not meters:
        return _installed("COPILOT", "detail.copilot_no_sub")
    return ProviderUsage(name="COPILOT", plan=plan, meters=meters)


def _detect_windsurf() -> bool:
    return _any_exists(_roaming("Windsurf"), _local("Programs", "Windsurf"), _local("windsurf")) or _cmd_exists("windsurf")


def _load_windsurf() -> ProviderUsage:
    db = _roaming("Windsurf", "User", "globalStorage", "state.vscdb")
    if db.exists():
        return _installed("WINDSURF", "detail.windsurf_panel")
    return _installed("WINDSURF", "detail.installed")


def _detect_antigravity() -> bool:
    return _any_exists(
        _local("Antigravity"),
        _local("google-antigravity"),
        _local("Google", "Antigravity"),
        _home(".antigravity"),
        _home(".config", "opencode", "antigravity-accounts.json"),
    ) or _cmd_exists("antigravity")


def _load_antigravity() -> ProviderUsage:
    return _installed("ANTIGRAVITY", "detail.installed")


def _detect_chatgpt() -> bool:
    return _any_exists(
        _roaming("ChatGPT"),
        _local("Programs", "ChatGPT"),
        _local("OpenAI"),
    )


def _load_chatgpt() -> ProviderUsage:
    if _home(".codex", "auth.json").exists():
        plan, meters = _codex_meters()
        return ProviderUsage(name="CHATGPT", plan=plan, meters=meters)
    return _installed("CHATGPT", "detail.chatgpt_login")


def _detect_continue() -> bool:
    return _any_exists(_home(".continue"), _roaming("Continue"))


def _load_continue() -> ProviderUsage:
    return _installed("CONTINUE", "detail.continue")


def _detect_trae() -> bool:
    return _any_exists(_roaming("Trae"), _local("Programs", "Trae"))


def _load_trae() -> ProviderUsage:
    return _installed("TRAE", "detail.trae")


def _detect_ollama() -> bool:
    return _cmd_exists("ollama") or _any_exists(_local("Programs", "Ollama"), _home(".ollama"))


def _load_ollama() -> ProviderUsage:
    return _unlimited("OLLAMA", "detail.local_no_internet")


def _detect_lmstudio() -> bool:
    return _cmd_exists("lmstudio") or _any_exists(_local("Programs", "LM Studio"), _roaming("LM Studio"))


def _load_lmstudio() -> ProviderUsage:
    return _unlimited("LM STUDIO", "detail.local_no_internet")


def _iso_reset(value: Any) -> str:
    if not value:
        return ""
    try:
        text = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        if dt.tzinfo:
            dt = dt.astimezone().replace(tzinfo=None)
        stamp = dt.timestamp()
        return _unix_reset(stamp)
    except (ValueError, TypeError, OSError):
        return ""


_PROVIDER_LOADERS = (
    ("CURSOR", _detect_cursor, _load_cursor),
    ("CODEX", _detect_codex, _load_codex),
    ("CLAUDE", _detect_claude, _load_claude),
    ("GEMINI", _detect_gemini, _load_gemini),
    ("COPILOT", _detect_copilot, _load_copilot),
    ("WINDSURF", _detect_windsurf, _load_windsurf),
    ("ANTIGRAVITY", _detect_antigravity, _load_antigravity),
    ("CHATGPT", _detect_chatgpt, _load_chatgpt),
    ("CONTINUE", _detect_continue, _load_continue),
    ("TRAE", _detect_trae, _load_trae),
    ("OLLAMA", _detect_ollama, _load_ollama),
    ("LM STUDIO", _detect_lmstudio, _load_lmstudio),
)

