"""Eski proje klasoru ve Pulse onbellegini sil."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

OLD_PROJECT = Path(r"D:\cursor\token takip programı")


def purge_legacy() -> list[str]:
    removed: list[str] = []
    pulse = Path(os.environ.get("LOCALAPPDATA", "")) / "Pulse"
    for path in (OLD_PROJECT, pulse):
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
            removed.append(str(path))
    return removed


if __name__ == "__main__":
    gone = purge_legacy()
    for line in gone:
        print("silindi:", line)
    if not gone:
        print("eski konum yok")
