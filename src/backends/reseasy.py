"""
ResEasy booking adapter.  >>> THIS IS THE ONLY FILE YOU EDIT. <<<

Implement `ReseasyBackend` (a `BookingBackend`) by mapping `ReseasyClient`
calls into the ABC's consistent return types, then self-register it under the
name "reseasy".

Read TASK.md for the full spec. Quick reference:

  get_availability   -> AvailabilityResult
  create_reservation -> (caller_message: str, provider_id: str)
  find_reservation   -> str
  modify_reservation -> str
  cancel_reservation -> str

Rules the grader enforces (see grade/RUBRIC.md):
  - Read credentials from the passed-in `BookingConfig`, never from the process
    environment or module globals.
  - Do NOT import anything from `livekit`.
  - Self-register with `register_backend("reseasy", <factory>, validator=...)`.
  - Do NOT edit base.py, registry.py, or the tests.
"""

from __future__ import annotations

import time

from backends.base import AvailabilityResult, BookingBackend
from backends.registry import BookingBackendError, register_backend
from backends.reseasy_client import (
    ReseasyClient,
    ReseasyConflict,
    ReseasyNotFound,
)


class ReseasyBackend(BookingBackend):
    def __init__(self, *, restaurant_id: str, client: ReseasyClient) -> None:
        self._restaurant_id = restaurant_id
        self._client = client

    async def get_availability(
        self,
        date: str,
        time_: str,
        party_size: int,
        *,
        preference: str = "balanced",
    ) -> AvailabilityResult:
        slots = await self._client.get_slots(date)
        available_slots = [s for s in slots if s["available"]]

        exact_match = next((s for s in available_slots if s["time"] == time_), None)
        exact_match_datetime = exact_match["iso"] if exact_match else None

        alternative_times = [
            s["time"] for s in available_slots if s["time"] != time_
        ] if not exact_match else []

        return AvailabilityResult(
            date=date,
            requested_time=time_,
            requested_hhmm=time_,
            party_size=party_size,
            exact_match_datetime=exact_match_datetime,
            alternative_times=alternative_times,
            fetched_at_monotonic=time.monotonic(),
            preference=preference,
        )

    async def create_reservation(
        self,
        reservation_id: str,
        date: str,
        time_: str,
        party_size: int,
        guest_name: str,
        guest_phone: str,
        guest_email: str = "",
        notes: str = "",
        locale: str = "en_US",
        restaurant_timezone: str = "UTC",
        prefetched_meal_date: str = "",
    ) -> tuple[str, str]:
        try:
            result = await self._client.create_booking(
                date=date,
                time_=time_,
                party_size=party_size,
                name=guest_name,
                phone=guest_phone,
                email=guest_email,
                notes=notes,
            )
            provider_id = result["id"]
            msg = (
                f"Your reservation is confirmed for {party_size} guests on {date} at {time_}. "
                f"Booking reference: {provider_id}."
            )
            return msg, provider_id
        except ReseasyConflict as exc:
            return f"BOOKING_ERROR: slot {date} {time_} is no longer available.", ""

    async def find_reservation(
        self,
        guest_phone: str,
        restaurant_timezone: str = "UTC",
    ) -> str:
        bookings = await self._client.find_by_phone(guest_phone)
        if not bookings:
            return f"No reservations found for {guest_phone}."
        lines = [
            f"- {b['date']} at {b['time']} for {b['party_size']} guests (ref: {b['id']})"
            for b in bookings
        ]
        return "Found reservations:\n" + "\n".join(lines)

    async def modify_reservation(
        self,
        reservation_id: str,
        new_date: str = "",
        new_time: str = "",
        new_party_size: int = 0,
        new_notes: str = "",
        restaurant_timezone: str = "UTC",
    ) -> str:
        # Nothing to change — skip API call
        if not new_date and not new_time and not new_party_size and not new_notes:
            return f"Reservation {reservation_id} is unchanged."

        kwargs: dict = {}
        if new_date:
            kwargs["date"] = new_date
        if new_time:
            kwargs["time_"] = new_time
        if new_party_size:
            kwargs["party_size"] = new_party_size
        if new_notes:
            kwargs["notes"] = new_notes

        try:
            await self._client.update_booking(reservation_id, **kwargs)
            return f"Reservation {reservation_id} has been updated successfully."
        except ReseasyNotFound:
            return f"BOOKING_ERROR: reservation {reservation_id} not found."

    async def cancel_reservation(
        self,
        reservation_id: str,
    ) -> str:
        try:
            await self._client.cancel_booking(reservation_id)
            return f"Reservation {reservation_id} has been cancelled."
        except ReseasyNotFound:
            return f"BOOKING_ERROR: reservation {reservation_id} not found."


# ---------------------------------------------------------------------------
# Factory + validator + registration
# ---------------------------------------------------------------------------

def _factory(cfg) -> ReseasyBackend:
    client = ReseasyClient(
        api_key=cfg.reseasy_api_key,
        base_url=cfg.reseasy_base_url,
    )
    return ReseasyBackend(restaurant_id=cfg.reseasy_restaurant_id, client=client)


def _validator(cfg) -> str | None:
    if not cfg.reseasy_api_key:
        return "reseasy_api_key is missing from BookingConfig"
    return None


register_backend("reseasy", _factory, validator=_validator)
