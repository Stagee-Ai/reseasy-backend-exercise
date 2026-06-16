"""
Booking-backend adapters.

Importing this package pulls in every provider module so each one runs its
`register_backend(...)` side effect at import time. New providers are added by
listing them below.
"""

from backends import reseasy  # noqa: F401 — import for registration side effect
