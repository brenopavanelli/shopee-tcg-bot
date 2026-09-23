from tcgbot import collector as collector_module
from tcgbot import publisher as publisher_module


def _patch_paths(monkeypatch, tmp_path):
    for mod in (collector_module, publisher_module):
        monkeypatch.setattr(mod, "HISTORY_PATH", tmp_path / "postados.json")
        monkeypatch.setattr(mod, "QUEUE_PATH", tmp_path / "fila.json")
    monkeypatch.setattr(collector_module, "KEYWORDS_STATE_PATH", tmp_path / "keywords_state.json")


def test_collect_fills_queue(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    added = collector_module.collect(shopee_dry_run=True)
    from tcgbot.queue_store import load_queue
    assert added == len(load_queue(tmp_path / "fila.json")) >= 1


def test_publish_pops_from_queue(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    collector_module.collect(shopee_dry_run=True)
    assert publisher_module.publish(shopee_dry_run=True, telegram_dry_run=True) is True
    from tcgbot.storage import load_history
    assert len(load_history(tmp_path / "postados.json")) == 1


def test_publish_collects_when_queue_empty(tmp_path, monkeypatch):
    _patch_paths(monkeypatch, tmp_path)
    assert publisher_module.publish(shopee_dry_run=True, telegram_dry_run=True) is True