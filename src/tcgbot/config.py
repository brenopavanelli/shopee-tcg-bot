from dotenv import load_dotenv
load_dotenv()

import os
from dataclasses import dataclass, field


def _get_float(name: str, default: float) -> float:
    return float(os.getenv(name, default))


def _get_int(name: str, default: int) -> int:
    return int(os.getenv(name, default))


def _get_list(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Config:
    min_rating_ideal: float = field(default_factory=lambda: _get_float("MIN_RATING_IDEAL", 4.8))
    min_rating_fallback: float = field(default_factory=lambda: _get_float("MIN_RATING_FALLBACK", 4.7))
    min_sales_ideal: int = field(default_factory=lambda: _get_int("MIN_SALES_IDEAL", 20))
    min_sales_fallback: int = field(default_factory=lambda: _get_int("MIN_SALES_FALLBACK", 10))
    title_dedup_days: int = field(default_factory=lambda: _get_int("TITLE_DEDUP_DAYS", 3))
    max_search_attempts: int = field(default_factory=lambda: _get_int("MAX_SEARCH_ATTEMPTS", 3))
    keywords: list[str] = field(default_factory=lambda: _get_list(
        "KEYWORDS",
        ["Pokemon TCG", "Pokemon booster box", "Pokemon Elite Trainer Box"],
    ))


config = Config()