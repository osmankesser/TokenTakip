"""release_out/TokenTracker -> proje köküne kopyala."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "release_out" / "TokenTracker"


def main() -> None:
    if not (SRC / "TokenTracker.exe").is_file():
        sys.exit(f"Once derleyin: {SRC} yok")
    lic = ROOT / "LISANS-SOZLESMESI.txt"
    if not lic.is_file():
        sys.exit("LISANS-SOZLESMESI.txt yok")
    for name in ("TokenTracker.exe", "_internal"):
        dst = ROOT / name
        src = SRC / name
        if dst.is_dir():
            shutil.rmtree(dst)
        elif dst.is_file():
            dst.unlink()
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        print(dst)
    print(lic)
    from _prune_exes import prune_exes

    for path in prune_exes():
        print("silindi:", path)


if __name__ == "__main__":
    main()
