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
        raise NotImplementedError("TODO: implement get_availability")

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
        raise NotImplementedError("TODO: implement create_reservation")

    async def find_reservation(
        self,
        guest_phone: str,
        restaurant_timezone: str = "UTC",
    ) -> str:
        raise NotImplementedError("TODO: implement find_reservation")

    async def modify_reservation(
        self,
        reservation_id: str,
        new_date: str = "",
        new_time: str = "",
        new_party_size: int = 0,
        new_notes: str = "",
        restaurant_timezone: str = "UTC",
    ) -> str:
        raise NotImplementedError("TODO: implement modify_reservation")

    async def cancel_reservation(
        self,
        reservation_id: str,
    ) -> str:
        raise NotImplementedError("TODO: implement cancel_reservation")


# ---------------------------------------------------------------------------
# Factory + validator + registration
# ---------------------------------------------------------------------------
# TODO: write a factory that builds a ReseasyBackend from a BookingConfig
#       (reading creds off the config object), an optional startup validator,
#       and a register_backend("reseasy", ...) call so the dispatcher can find
#       your backend without any edits to registry.py.
