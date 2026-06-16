#!/usr/bin/env python3
"""Regenerate grade/manifest.json — sha256 of the read-only files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READ_ONLY = [
    "src/backends/base.py",
    "src/backends/registry.py",
    "src/backends/reseasy_client.py",
    "tests/test_contract.py",
]


def main() -> None:
    manifest = {
        rel: hashlib.sha256((ROOT / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        for rel in READ_ONLY
    }
    out = Path(__file__).resolve().parent / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(manifest)} files)")


if __name__ == "__main__":
    main()
