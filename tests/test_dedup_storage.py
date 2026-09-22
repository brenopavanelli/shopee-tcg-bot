from datetime import datetime, timedelta, timezone
from tcgbot.dedup import normalize_title, is_duplicate
from tcgbot.storage import prune_old, save_history, load_history


def test_normalize_title_strips_accents_emoji_punct():
    assert normalize_title("Pokémon TCG — Booster Box! 🔥") == "pokemon tcg booster box"


def test_is_duplicate_by_item_id():
    history = [{"item_id": 123, "normalized_title": "outro titulo"}]
    dup, reason = is_duplicate(123, "titulo qualquer", history)
    assert dup is True
    assert "item_id" in reason


def test_is_duplicate_by_normalized_title():
    history = [{"item_id": 999, "normalized_title": "pokemon booster box"}]
    dup, reason = is_duplicate(1, "pokemon booster box", history)
    assert dup is True


def test_not_duplicate_when_no_match():
    history = [{"item_id": 999, "normalized_title": "outra coisa"}]
    dup, _ = is_duplicate(1, "pokemon booster box", history)
    assert dup is False


def test_prune_old_removes_expired_records():
    now = datetime.now(timezone.utc)
    old = {"published_at": (now - timedelta(days=5)).isoformat()}
    recent = {"published_at": (now - timedelta(days=1)).isoformat()}
    kept = prune_old([old, recent], days=3, now=now)
    assert kept == [recent]


def test_save_and_load_history_roundtrip(tmp_path):
    path = tmp_path / "postados.json"
    records = [{"item_id": 1, "normalized_title": "x", "published_at": "2026-01-01T00:00:00+00:00"}]
    save_history(path, records)
    assert load_history(path) == records