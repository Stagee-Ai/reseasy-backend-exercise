# Take-home: add a booking backend

This is a self-contained slice of our voice-agent's booking layer. You will add
support for a new (fictional) reservation provider, **ResEasy**, by implementing
one adapter against a stable interface — the same way we add real providers
(TheFork, CoverManager, SevenRooms) to the production system.

We care less about lines of code than about whether you respect the seams:
backends plug in behind an interface, tenant credentials come from config (never
from the environment), and business logic stays free of any framework.

## Setup

```bash
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                                            # contract tests (red until you implement)
```

## Your task

Read **[TASK.md](TASK.md)**. In short: implement `ReseasyBackend` in
`src/backends/reseasy.py` (the only file you edit) and self-register it so the
dispatcher can find it.

## How you'll be graded

Grading is automated and objective. Run it yourself any time:

```bash
python grade/grade.py
```

It scores five areas out of 100 — behavioral contract, self-registration,
tenant isolation, framework boundary, and file integrity. The full rubric is in
[grade/RUBRIC.md](grade/RUBRIC.md). A strong submission scores 100.

## Rules

- Edit **only** `src/backends/reseasy.py`. Files marked `DO NOT EDIT` are checked
  for tampering by the grader.
- Don't add third-party dependencies beyond `requirements.txt`.
- Treat `ReseasyClient` as an opaque SDK — call its methods, don't reach inside.

## What to submit

Your edited `reseasy.py`, plus a short `NOTES.md` (a few sentences): any
assumptions you made, and how adding a *second* future provider would differ
from editing your file.
