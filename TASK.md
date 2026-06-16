# TASK — implement the ResEasy booking backend

You're integrating **ResEasy**, a fictional reservation provider. Its SDK is
already written for you: `src/backends/reseasy_client.py` (an in-memory
simulator you can run offline). Your job is the *adapter* that maps ResEasy's
shapes onto our backend interface so the rest of the system never has to know
ResEasy exists.

Implement `ReseasyBackend` in **`src/backends/reseasy.py`** — the only file you
touch.

## The interface (`BookingBackend`)

Every method must return the type below. The dispatcher and the contract tests
rely on these exact shapes; never raise out of these methods for an expected
provider failure (unknown id, taken slot) — return a caller-facing string or a
`BOOKING_ERROR:` message instead.

| Method | Returns | Notes |
|---|---|---|
| `get_availability(date, time_, party_size, *, preference)` | `AvailabilityResult` | exact match if that time is open, otherwise list other open times as `alternative_times` |
| `create_reservation(reservation_id, date, time_, party_size, guest_name, guest_phone, ...)` | `tuple[str, str]` | `(caller_message, provider_id)`; a success message must contain the word **confirmed** |
| `find_reservation(guest_phone, ...)` | `str` | caller-facing summary; a non-empty "none found" string is valid |
| `modify_reservation(reservation_id, new_date, new_time, new_party_size, new_notes, ...)` | `str` | if nothing changed, return a message containing **unchanged** without calling the API |
| `cancel_reservation(reservation_id)` | `str` | non-empty caller-facing message |

`AvailabilityResult` (see `base.py`) fields you set:
`date`, `requested_time`, `requested_hhmm`, `party_size`,
`exact_match_datetime` (the provider's ISO string, or `None`),
`alternative_times` (list of `"HH:MM"`), `fetched_at_monotonic` (`time.monotonic()`).
There's a `render_availability_message(result)` helper if you want it.

## The ResEasy SDK (`ReseasyClient`)

Async methods — call these, map the results:

```python
await client.get_slots(date)            # -> [{"iso","time","available"}, ...]
await client.create_booking(date=, time_=, party_size=, name=, phone=, email="", notes="")
                                        # -> {"id","status","iso"}; raises ReseasyConflict if slot taken
await client.find_by_phone(phone)       # -> [{"id","date","time","party_size"}, ...]
await client.update_booking(id, date=None, time_=None, party_size=None, notes=None)
                                        # -> {...}; raises ReseasyNotFound
await client.cancel_booking(id)         # -> {"id","status"}; raises ReseasyNotFound
```

Exceptions to catch: `ReseasyConflict`, `ReseasyNotFound` (both subclasses of
`ReseasyError`).

## Wiring it in (self-registration)

The dispatcher resolves a backend with `get_backend(cfg.backend, cfg)` and never
branches on provider name. For that to find ResEasy, your file must, at import
time, call:

```python
register_backend("reseasy", <factory>, validator=<optional>)
```

- The **factory** takes a `BookingConfig` and returns a `ReseasyBackend`. Read
  credentials (`reseasy_api_key`, `reseasy_base_url`, `reseasy_restaurant_id`)
  off that config object and pass them into a `ReseasyClient`. **Never** read
  `os.environ` / `os.getenv` here — credentials are per-tenant and live on the
  config.
- The optional **validator** does a cheap, no-network startup check (e.g. key
  present) and returns `None` when OK or an error string otherwise.

`ReseasyBackend.__init__` already accepts a `client=` so tests can inject a
seeded simulator; your factory constructs the real client from config.

## Constraints (these are graded)

1. **Tenant isolation** — creds come from the passed-in `BookingConfig`, not the
   environment or module globals.
2. **No backend branching** — you don't (and can't) edit the dispatcher or
   registry; registration is how you plug in.
3. **Framework boundary** — the adapter must not import anything from `livekit`
   (or any web framework). It's pure business logic.
4. **Don't touch** `base.py`, `registry.py`, `reseasy_client.py`, or the tests.

## Definition of done

`python grade/grade.py` reports 100/100, and `NOTES.md` answers: how would
adding a *second* new provider differ from what you just did?
