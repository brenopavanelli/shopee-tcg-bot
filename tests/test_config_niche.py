"""Tests for SHOPEE_NICHE / KEYWORDS config wiring into the curated catalog."""
from tcgbot import config as config_mod
from tcgbot import niches
from tcgbot.niches import resolve_keywords


def test_keywords_env_does_not_change_resolver(monkeypatch):
    monkeypatch.setenv("KEYWORDS", "Poke A, Poke B")
    # resolve_keywords is niche-driven; KEYWORDS only matters in Config.
    kw = resolve_keywords("yugioh")
    assert "Yu-Gi-Oh" in " ".join(kw)


def test_config_prefers_explicit_keywords(monkeypatch):
    monkeypatch.setenv("KEYWORDS", "Alpha, Beta")
    monkeypatch.delenv("SHOPEE_NICHE", raising=False)
    cfg = config_mod.Config()
    assert cfg.keywords == ["Alpha", "Beta"]


def test_config_uses_niche_when_no_keywords(monkeypatch):
    monkeypatch.delenv("KEYWORDS", raising=False)
    monkeypatch.setenv("SHOPEE_NICHE", "one-piece")
    cfg = config_mod.Config()
    assert cfg.keywords == list(niches.ONE_PIECE.keywords)


def test_config_default_niche_is_pokemon(monkeypatch):
    monkeypatch.delenv("KEYWORDS", raising=False)
    monkeypatch.delenv("SHOPEE_NICHE", raising=False)
    cfg = config_mod.Config()
    assert cfg.keywords == list(niches.POKEMON.keywords)


def test_config_case_insensitive_niche(monkeypatch):
    monkeypatch.delenv("KEYWORDS", raising=False)
    monkeypatch.setenv("SHOPEE_NICHE", "YU-GI-OH")
    cfg = config_mod.Config()
    assert cfg.keywords == list(niches.YUGIOH.keywords)