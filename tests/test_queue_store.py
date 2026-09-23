from datetime import datetime, timedelta, timezone
from tcgbot.models import Offer
from tcgbot.queue_store import prune_expired, enqueue, pop_next


def _offer(item_id=1):
    return Offer(item_id=item_id, shop_id=1, title="Produto Teste", price=10.0,
                 rating=4.9, sales=50, shop_type=[1], image_url="http://x/i.jpg",
                 product_link="http://x/p", offer_link="http://x/o")


def test_enqueue_avoids_duplicate_item_id():
    queue = enqueue(enqueue([], _offer(1), "kw"), _offer(1), "kw")
    assert len(queue) == 1


def test_pop_next_returns_first_and_rest():
    queue = enqueue(enqueue([], _offer(1), "kw"), _offer(2), "kw")
    item, rest = pop_next(queue)
    assert item["offer"]["item_id"] == 1
    assert len(rest) == 1


def test_prune_expired_removes_old_items():
    now = datetime.now(timezone.utc)
    queue = [
        {"offer": _offer(1).__dict__, "keyword": "kw", "queued_at": (now - timedelta(hours=10)).isoformat()},
        {"offer": _offer(2).__dict__, "keyword": "kw", "queued_at": (now - timedelta(hours=1)).isoformat()},
    ]
    kept = prune_expired(queue, max_age_hours=6, now=now)
    assert len(kept) == 1 and kept[0]["offer"]["item_id"] == 2