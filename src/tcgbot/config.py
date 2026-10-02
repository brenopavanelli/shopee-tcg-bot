from dotenv import load_dotenv

load_dotenv()

import os
from dataclasses import dataclass, field

from tcgbot.niches import resolve_keywords


def _get_float(name: str, default: float) -> float:
    return float(os.getenv(name, default))


def _get_int(name: str, default: int) -> int:
    return int(os.getenv(name, default))


def _get_list(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


def _default_keywords() -> list[str]:
    """Keywords from `KEYWORDS` env, else the curated list for `SHOPEE_NICHE`.

    ``SHOPEE_NICHE`` selects a curated keyword bundle from the ``niches``
    package (default ``pokemon``). An explicit ``KEYWORDS`` env var always
    wins, so existing deployments keep working unchanged.
    """
    explicit = _get_list("KEYWORDS", [])
    if explicit:
        return explicit
    niche = (os.getenv("SHOPEE_NICHE") or "pokemon").strip().lower()
    return resolve_keywords(niche)


@dataclass(frozen=True)
class Config:
    queue_max_age_hours: int = field(default_factory=lambda: _get_int("QUEUE_MAX_AGE_HOURS", 6))
    min_rating_ideal: float = field(default_factory=lambda: _get_float("MIN_RATING_IDEAL", 4.8))
    min_rating_fallback: float = field(default_factory=lambda: _get_float("MIN_RATING_FALLBACK", 4.7))
    min_sales_ideal: int = field(default_factory=lambda: _get_int("MIN_SALES_IDEAL", 20))
    min_sales_fallback: int = field(default_factory=lambda: _get_int("MIN_SALES_FALLBACK", 10))
    title_dedup_days: int = field(default_factory=lambda: _get_int("TITLE_DEDUP_DAYS", 3))
    max_search_attempts: int = field(default_factory=lambda: _get_int("MAX_SEARCH_ATTEMPTS", 3))
    keywords: list[str] = field(default_factory=_default_keywords)


config = Config()