# NOTES

## Assumptions

- `ReseasyClient.update_booking` accepts `notes` as a keyword arg — confirmed via the SDK signature.
- `alternative_times` is only populated when exact match fails; when exact match succeeds it stays empty (contract tests confirm this is correct).
- Validator flags a missing `reseasy_api_key` at startup — a cheap, no-network check per the spec.
- `new_party_size=0` is treated as "no change" (zero is falsy; the interface default is 0).

## Adding a second provider

Create `src/backends/<provider>.py`, implement `BookingBackend`, and call `register_backend("<name>", factory, validator=...)` at module import time. That's the entire diff. The dispatcher, registry, and all existing backends are untouched — the seam is the interface + registry, so each new adapter is fully self-contained.
