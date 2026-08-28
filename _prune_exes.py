"""Tek guncel dagitim: D:\\token tracker\\TokenTracker.exe (+ _internal)."""
from __future__ import annotations

import shutil
from pathlib import Path

CANONICAL = Path(r"D:\token tracker")
CANONICAL_EXE = CANONICAL / "TokenTracker.exe"
EXE_NAMES = frozenset({"TokenTracker.exe", "TokenTakip.exe", "PulseTokenTakip.exe"})
INTERNAL_DIR = "_internal"
SKIP_PARTS = frozenset({".venv", ".venv_release", "site-packages", "pip"})


def _is_deploy_internal(path: Path) -> bool:
    if path.name != INTERNAL_DIR:
        return False
    if SKIP_PARTS.intersection(path.parts):
        return False
    parent = path.parent
    if any((parent / name).is_file() for name in EXE_NAMES):
        return True
    return parent.name in {"TokenTracker", "TokenTakip"} or "-win64" in parent.name

# ponytail: yalnizca ara build ciktisi
STALE_ROOTS = (CANONICAL / "release_out",)


def prune_exes(*, keep_canonical: bool = True) -> list[str]:
    removed: list[str] = []
    if keep_canonical and not CANONICAL_EXE.is_file():
        return removed

    for root in STALE_ROOTS:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if path.is_file() and path.name in EXE_NAMES:
                path.unlink(missing_ok=True)
                removed.append(str(path))
            elif _is_deploy_internal(path):
                shutil.rmtree(path, ignore_errors=True)
                removed.append(str(path))

    staged = CANONICAL / "release_out" / "TokenTracker"
    if staged.is_dir():
        shutil.rmtree(staged, ignore_errors=True)
        removed.append(str(staged))
    return removed


if __name__ == "__main__":
    gone = prune_exes(keep_canonical=False)
    for line in gone:
        print("silindi:", line)
    if not gone:
        print("eski exe yok")
