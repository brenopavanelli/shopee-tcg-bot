import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tcgbot.models import Offer


def load_queue(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_queue(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def prune_expired(items: list[dict], max_age_hours: int, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=max_age_hours)
    return [i for i in items if datetime.fromisoformat(i["queued_at"]) >= cutoff]


def enqueue(items: list[dict], offer: Offer, keyword: str, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    if any(i["offer"]["item_id"] == offer.item_id for i in items):
        return items
    items.append({"offer": asdict(offer), "keyword": keyword, "queued_at": now.isoformat()})
    return items


def pop_next(items: list[dict]) -> tuple[dict | None, list[dict]]:
    if not items:
        return None, items
    next_item, *rest = items
    return next_item, rest