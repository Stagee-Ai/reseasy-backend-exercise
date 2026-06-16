"""
Minimal per-tenant config stand-in for the exercise.

In the real codebase this is a pydantic `BookingConfig` nested inside a
`RestaurantConfig` loaded once per call. Here it is a plain dataclass with the
fields your ResEasy backend needs. Tenant credentials live HERE, scoped to one
restaurant — never in process globals / environment lookups inside the adapter.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BookingConfig:
    backend: str = "reseasy"
    # ResEasy per-tenant settings — read these in your factory.
    reseasy_api_key: str = ""
    reseasy_base_url: str = "https://api.reseasy.example"
    reseasy_restaurant_id: str = ""
