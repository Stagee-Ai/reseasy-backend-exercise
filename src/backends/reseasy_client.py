"""
ResEasy API client (PROVIDED — you do not need to change this).

ResEasy is a fictional reservation provider for this exercise. This module is
an in-memory simulator of its HTTP API so you can develop and test offline.
Treat it as an opaque SDK: call its async methods, map the results into the
`BookingBackend` return types. Do not reach past these methods.

All times are local clock strings ("HH:MM"); `iso` fields are the provider's
canonical slot datetimes (what you must surface as `exact_match_datetime`).

>>> You should not need to edit this file. <<<
"""

from __future__ import annotations


class ReseasyError(RuntimeError):
    """Base error for ResEasy API failures."""


class ReseasyConflict(ReseasyError):
    """Raised by create_booking when the requested slot is no longer available."""


class ReseasyNotFound(ReseasyError):
    """Raised by update/cancel when no booking matches the given id."""


# Default seed: a single open day so the simulator is usable out of the box.
_DEFAULT_SLOTS: dict[str, list[dict]] = {
    "2026-05-01": [
        {"iso": "2026-05-01T19:00:00+01:00", "time": "19:00", "available": True},
        {"iso": "2026-05-01T19:30:00+01:00", "time": "19:30", "available": True},
        {"iso": "2026-05-01T20:00:00+01:00", "time": "20:00", "available": True},
    ],
}


class ReseasyClient:
    """In-memory ResEasy client.

    Construct with credentials in production; the simulator ignores them but
    your factory must still pass them through (the grader checks that creds are
    read from config, never from process globals).
    """

    def __init__(
        self,
        *,
        api_key: str = "",
        base_url: str = "https://api.reseasy.example",
        seed_slots: dict[str, list[dict]] | None = None,
        seed_bookings: dict[str, dict] | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        # date -> list of {"iso","time","available"}
        self._slots: dict[str, list[dict]] = seed_slots or {
            d: [dict(s) for s in slots] for d, slots in _DEFAULT_SLOTS.items()
        }
        # booking_id -> {"id","date","time","party_size","name","phone"}
        self._bookings: dict[str, dict] = dict(seed_bookings or {})
        self._seq = 0

    # -- reads -------------------------------------------------------------

    async def get_slots(self, date: str) -> list[dict]:
        """Return all slots for `date`: [{"iso","time","available"}, ...]."""
        return [dict(s) for s in self._slots.get(date, [])]

    async def find_by_phone(self, phone: str) -> list[dict]:
        """Return bookings for a phone: [{"id","date","time","party_size"}, ...]."""
        return [
            {k: b[k] for k in ("id", "date", "time", "party_size")}
            for b in self._bookings.values()
            if b["phone"] == phone
        ]

    # -- writes ------------------------------------------------------------

    async def create_booking(
        self,
        *,
        date: str,
        time_: str,
        party_size: int,
        name: str,
        phone: str,
        email: str = "",
        notes: str = "",
    ) -> dict:
        """Book a slot. Returns {"id","status","iso"}; raises ReseasyConflict
        if the slot for (date, time_) is missing or already taken."""
        slot = next(
            (s for s in self._slots.get(date, []) if s["time"] == time_ and s["available"]),
            None,
        )
        if slot is None:
            raise ReseasyConflict(f"slot {date} {time_} not available")
        slot["available"] = False
        self._seq += 1
        booking_id = f"re_{self._seq:04d}"
        self._bookings[booking_id] = {
            "id": booking_id,
            "date": date,
            "time": time_,
            "party_size": party_size,
            "name": name,
            "phone": phone,
        }
        return {"id": booking_id, "status": "confirmed", "iso": slot["iso"]}

    async def update_booking(
        self,
        booking_id: str,
        *,
        date: str | None = None,
        time_: str | None = None,
        party_size: int | None = None,
        notes: str | None = None,
    ) -> dict:
        """Patch a booking. Raises ReseasyNotFound if id is unknown."""
        booking = self._bookings.get(booking_id)
        if booking is None:
            raise ReseasyNotFound(booking_id)
        if date is not None:
            booking["date"] = date
        if time_ is not None:
            booking["time"] = time_
        if party_size is not None:
            booking["party_size"] = party_size
        return dict(booking)

    async def cancel_booking(self, booking_id: str) -> dict:
        """Cancel a booking. Raises ReseasyNotFound if id is unknown."""
        booking = self._bookings.pop(booking_id, None)
        if booking is None:
            raise ReseasyNotFound(booking_id)
        return {"id": booking_id, "status": "cancelled"}
