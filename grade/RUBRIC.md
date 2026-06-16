# Rubric — ResEasy backend exercise

`python grade/grade.py` produces the score. Areas and weights:

| Area | Pts | Auto-check | What it proves |
|---|---:|---|---|
| Behavioral contract | 55 | `pytest tests/test_contract.py`, score ∝ tests passed | The adapter actually maps ResEasy → the ABC types correctly (availability exact/alternatives, confirmed-message, no-changes "unchanged", graceful unknown-id handling). |
| Self-registration | 15 | `get_backend("reseasy", cfg)` returns a `BookingBackend` | They plugged in via the registry, not by editing the dispatcher. |
| Tenant isolation | 15 | 8: no `os.getenv`/`os.environ` in adapter · 7: a sentinel `api_key` set on config reaches the constructed client | Creds are per-tenant, sourced from config (Sin #2). |
| Framework boundary | 5 | no `import livekit` / `from livekit` in the adapter | Business logic stays framework-free. |
| File integrity | 10 | sha256 of read-only files vs `manifest.json` | They solved the problem instead of editing the tests/interface. |

Pass bar: **≥ 85** with the full contract green. 100 is expected from a strong
candidate — this is a focused task, not a trick.

## Signal beyond the number (read the diff + NOTES.md)

The score tells you *correct*; the diff tells you *how they think*. Look for:

- **The "second provider" answer in NOTES.md.** The whole point of this design
  is that adding provider #2 is "another file + one `register_backend` call,
  zero edits elsewhere." If they articulate that, they understood the seam. If
  they describe touching shared code, they didn't.
- **Error mapping.** Did they catch `ReseasyConflict` / `ReseasyNotFound` and
  return caller-facing strings, or let exceptions escape (which would crash a
  live call)? The contract catches the obvious cases; skim for the rest.
- **No leaked details.** Provider-specific fields (`iso`, raw ids, status codes)
  should be translated, not handed upward verbatim.
- **The validator.** Optional, but writing a sensible no-network one is a sign
  they read the "fail fast at startup, not mid-call" intent.

## Red flags (investigate even if the score is high)

- Hardcoded slot/booking data to satisfy a specific test instead of mapping the
  client.
- Reaching into `client._slots` / `client._bookings` (private state) rather than
  the documented async methods.
- Reproducing the dispatcher logic inside the adapter (branching on name).

## Regenerating the integrity manifest

If you intentionally change a read-only file, refresh the hashes:

```bash
python grade/make_manifest.py
```
