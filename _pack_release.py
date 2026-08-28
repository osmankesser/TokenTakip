"""Yayin ZIP: release/TokenTracker-0.1.2-win64.zip"""
from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

from version import VERSION

ROOT = Path(__file__).resolve().parent
NAME = f"TokenTracker-{VERSION}-win64"
DOCS = ("LISANS-SOZLESMESI.txt", "LICENSE", "README.md", "SURUM-NOTLARI.txt")


def main() -> int:
    exe = ROOT / "TokenTracker.exe"
    internal = ROOT / "_internal"
    if not exe.is_file() or not internal.is_dir():
        print("Once _build_deploy.py calistirin", flush=True)
        return 1
    release = ROOT / "release"
    stage = release / NAME
    if stage.is_dir():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    shutil.copy2(exe, stage / "TokenTracker.exe")
    shutil.copytree(internal, stage / "_internal")
    for doc in DOCS:
        src = ROOT / doc
        if src.is_file():
            shutil.copy2(src, stage / doc)
    zip_path = release / f"{NAME}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in stage.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(release))
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    (release / f"{NAME}.sha256.txt").write_text(f"{digest}  {zip_path.name}\n", encoding="utf-8")
    print(zip_path)
    print(release / f"{NAME}.sha256.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
