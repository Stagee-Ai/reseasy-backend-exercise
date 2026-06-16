#!/usr/bin/env python3
"""
Automated grader for the ResEasy backend exercise.

    python grade/grade.py            # human-readable scorecard
    python grade/grade.py --json     # machine-readable

Scores five areas (100 pts):
  - Behavioral contract  (55)  pytest tests/test_contract.py
  - Self-registration    (15)  get_backend("reseasy", cfg) resolves with no dispatcher edits
  - Tenant isolation     (15)  no os.getenv/os.environ in adapter + creds flow from config
  - Framework boundary    (5)  adapter imports nothing from `livekit`
  - File integrity       (10)  read-only files (base/registry/test/client) unchanged
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
ADAPTER = SRC / "backends" / "reseasy.py"
sys.path.insert(0, str(SRC))

READ_ONLY = {
    "src/backends/base.py": None,
    "src/backends/registry.py": None,
    "src/backends/reseasy_client.py": None,
    "tests/test_contract.py": None,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# 1. Behavioral contract (55)
# ---------------------------------------------------------------------------
def grade_contract() -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_contract.py", "-q", "--no-header"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    out = proc.stdout + proc.stderr
    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", out)) else 0
    failed = int(m.group(1)) if (m := re.search(r"(\d+) failed", out)) else 0
    errors = int(m.group(1)) if (m := re.search(r"(\d+) error", out)) else 0
    total = passed + failed + errors
    score = round(55 * passed / total) if total else 0
    return {
        "area": "Behavioral contract",
        "max": 55,
        "score": score,
        "detail": f"{passed}/{total or '?'} contract tests passed"
        + (f", {errors} import/collection error(s)" if errors else ""),
    }


# ---------------------------------------------------------------------------
# 2. Self-registration + dispatch (15)
# ---------------------------------------------------------------------------
def grade_registration() -> dict:
    try:
        import backends  # noqa: F401 — triggers reseasy registration side effect
        from backends.base import BookingBackend
        from backends.registry import get_backend
        from config import BookingConfig

        backend = get_backend("reseasy", BookingConfig())
        ok = isinstance(backend, BookingBackend)
        return {
            "area": "Self-registration",
            "max": 15,
            "score": 15 if ok else 0,
            "detail": "get_backend('reseasy', cfg) returned a BookingBackend"
            if ok
            else "resolved object is not a BookingBackend",
        }
    except Exception as exc:
        return {
            "area": "Self-registration",
            "max": 15,
            "score": 0,
            "detail": f"dispatch failed: {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# 3. Tenant isolation (15)
# ---------------------------------------------------------------------------
def _find_sentinel(obj, needle: str, depth: int = 2) -> bool:
    if depth < 0:
        return False
    for value in vars(obj).values() if hasattr(obj, "__dict__") else []:
        if value == needle:
            return True
        if hasattr(value, "__dict__") and _find_sentinel(value, needle, depth - 1):
            return True
    return False


def _reads_process_env(src: str) -> bool:
    """True if the code (ignoring comments/strings) uses os.getenv/os.environ."""
    import io
    import token as tok
    import tokenize

    toks = [
        t for t in tokenize.generate_tokens(io.StringIO(src).readline)
        if t.type not in (tok.COMMENT, tok.STRING, tok.NL, tok.NEWLINE, tok.INDENT, tok.DEDENT)
    ]
    for i in range(len(toks) - 2):
        a, b, c = toks[i], toks[i + 1], toks[i + 2]
        if (
            a.type == tok.NAME and a.string == "os"
            and b.type == tok.OP and b.string == "."
            and c.type == tok.NAME and c.string in ("getenv", "environ")
        ):
            return True
    return False


def grade_isolation() -> dict:
    src = ADAPTER.read_text(encoding="utf-8")
    no_globals = not _reads_process_env(src)
    score = 8 if no_globals else 0
    notes = [
        "no os.getenv/os.environ in adapter" if no_globals else
        "FAIL: adapter reads process env (Sin #2 — read creds from config)"
    ]
    try:
        import backends  # noqa: F401
        from backends.registry import get_backend
        from config import BookingConfig

        cfg = BookingConfig(reseasy_api_key="SENTINEL-KEY-123")
        backend = get_backend("reseasy", cfg)
        flows = _find_sentinel(backend, "SENTINEL-KEY-123")
        score += 7 if flows else 0
        notes.append(
            "creds flow config -> backend" if flows
            else "WARN: config api_key not found on backend (did the factory pass it through?)"
        )
    except Exception as exc:
        notes.append(f"WARN: could not verify cred flow ({type(exc).__name__})")
    return {"area": "Tenant isolation", "max": 15, "score": score, "detail": "; ".join(notes)}


# ---------------------------------------------------------------------------
# 4. Framework boundary (5)
# ---------------------------------------------------------------------------
def grade_boundary() -> dict:
    src = ADAPTER.read_text(encoding="utf-8")
    clean = not re.search(r"\b(import\s+livekit|from\s+livekit)\b", src)
    return {
        "area": "Framework boundary",
        "max": 5,
        "score": 5 if clean else 0,
        "detail": "no livekit import in adapter" if clean
        else "FAIL: adapter imports livekit (business logic must stay framework-free)",
    }


# ---------------------------------------------------------------------------
# 5. File integrity (10)
# ---------------------------------------------------------------------------
def grade_integrity() -> dict:
    manifest_path = Path(__file__).resolve().parent / "manifest.json"
    if not manifest_path.exists():
        return {"area": "File integrity", "max": 10, "score": 10,
                "detail": "no manifest — skipped (run with the shipped manifest.json)"}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    changed = [rel for rel, want in manifest.items() if _sha256(ROOT / rel) != want]
    return {
        "area": "File integrity",
        "max": 10,
        "score": 10 if not changed else 0,
        "detail": "read-only files unchanged" if not changed
        else f"FAIL: edited read-only file(s): {', '.join(changed)}",
    }


def main() -> int:
    results = [
        grade_contract(),
        grade_registration(),
        grade_isolation(),
        grade_boundary(),
        grade_integrity(),
    ]
    total = sum(r["score"] for r in results)
    out_of = sum(r["max"] for r in results)

    if "--json" in sys.argv:
        print(json.dumps({"total": total, "out_of": out_of, "areas": results}, indent=2))
        return 0

    print("\n  ResEasy backend exercise — scorecard")
    print("  " + "-" * 58)
    for r in results:
        bar = f"{r['score']:>3}/{r['max']:<3}"
        print(f"  {bar}  {r['area']:<22} {r['detail']}")
    print("  " + "-" * 58)
    print(f"  {total:>3}/{out_of:<3}  TOTAL\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
