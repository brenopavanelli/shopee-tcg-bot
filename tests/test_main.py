from tcgbot import main as main_module


def test_run_dry_run_publishes_and_saves_history(tmp_path, monkeypatch):
    monkeypatch.setattr(main_module, "HISTORY_PATH", tmp_path / "postados.json")
    monkeypatch.setattr(main_module, "KEYWORDS_STATE_PATH", tmp_path / "keywords_state.json")

    main_module.run(dry_run=True)

    from tcgbot.storage import load_history
    history = load_history(tmp_path / "postados.json")
    assert len(history) == 1
    assert history[0]["item_id"] == 27391045821


def test_run_does_not_republish_same_item(tmp_path, monkeypatch):
    monkeypatch.setattr(main_module, "HISTORY_PATH", tmp_path / "postados.json")
    monkeypatch.setattr(main_module, "KEYWORDS_STATE_PATH", tmp_path / "keywords_state.json")

    main_module.run(dry_run=True)
    main_module.run(dry_run=True)  # segunda execução, mesmo produto

    from tcgbot.storage import load_history
    history = load_history(tmp_path / "postados.json")
    assert len(history) == 1  # não duplicou