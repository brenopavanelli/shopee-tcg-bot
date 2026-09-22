import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def load_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_history(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def prune_old(records: list[dict], days: int, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    kept = []
    for r in records:
        published_at = datetime.fromisoformat(r["published_at"])
        if published_at >= cutoff:
            kept.append(r)
    return kept


def build_record(offer, keyword: str, normalized_title: str, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    return {
        "item_id": offer.item_id,
        "shop_id": offer.shop_id,
        "title": offer.title,
        "normalized_title": normalized_title,
        "published_at": now.isoformat(),
        "price": offer.price,
        "discount_rate": offer.discount_rate,
        "keyword": keyword,
        "offer_link": offer.offer_link,
    }