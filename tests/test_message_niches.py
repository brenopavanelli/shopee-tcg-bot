import json
from pathlib import Path

import pytest

from tcgbot import niches
from tcgbot.message import _CAPTION_LIMIT, _price_block, build_message
from tcgbot.models import Offer

FIXTURE = Path(__file__).parent / "fixtures" / "product_offer_sample.json"


def _load_offer(index: int) -> Offer:
    data = json.loads(FIXTURE.read_text())
    node = data["data"]["productOfferV2"]["nodes"][index]
    return Offer.from_api_node(node)


# --- niche catalog -----------------------------------------------------------

def test_known_niches_include_default():
    names = niches.known_niches()
    assert "pokemon" in names
    assert "yugioh" in names
    assert "one-piece" in names


def test_resolve_keywords_default_is_pokemon():
    kw = niches.resolve_keywords(None)
    assert kw == list(niches.POKEMON.keywords)
    assert "Pokemon TCG" in kw
    # curated list is broader than the old 3-keyword default
    assert len(kw) >= 5


def test_resolve_keywords_selects_niche():
    kw = niches.resolve_keywords("yugioh")
    assert all("Yu-Gi-Oh" in k for k in kw)
    assert niches.resolve_keywords("one-piece") == list(niches.ONE_PIECE.keywords)


def test_resolve_keywords_unknown_niche_raises():
    with pytest.raises(KeyError):
        niches.resolve_keywords("not-a-game")


def test_niches_are_frozen():
    with pytest.raises(Exception):
        niches.POKEMON.keywords.append("hack")


# --- message: division-by-zero guard ------------------------------------------

def test_price_block_no_discount():
    offer = _load_offer(1)  # discount 0
    assert _price_block(offer).startswith("💵 R$ 289.00")


def test_price_block_guards_discount_over_99():
    # discount_rate >= 100 would crash naive `price / (1 - rate/100)`
    offer = _load_offer(0)
    offer = offer.__class__(
        **{**offer.__dict__, "discount_rate": 120}
    )
    block = _price_block(offer)
    assert "R$" in block
    # reported rate kept as-is
    assert "-120%" in block


# --- message: link is never truncated -----------------------------------------

def test_message_contains_full_link():
    offer = _load_offer(0)
    msg = build_message(offer)
    assert offer.offer_link in msg
    assert len(msg) <= _CAPTION_LIMIT


def test_message_link_survives_extreme_length():
    # absurdly long title forces overflow, but the link must remain intact
    offer = _load_offer(0)
    offer = offer.__class__(**{**offer.__dict__, "title": "P" * 5000})
    msg = build_message(offer)
    assert offer.offer_link in msg
    assert len(msg) <= _CAPTION_LIMIT
    # the message's final line is the full clickable URL
    assert msg.strip().endswith(offer.offer_link)


def test_message_link_survives_long_price_block():
    offer = _load_offer(0)
    offer = offer.__class__(**{**offer.__dict__, "price": 123456.78, "discount_rate": 99})
    msg = build_message(offer)
    assert offer.offer_link in msg
    assert len(msg) <= _CAPTION_LIMIT


def test_message_with_missing_links_falls_back_to_product_link():
    offer = _load_offer(0)
    offer = offer.__class__(**{**offer.__dict__, "offer_link": ""})
    msg = build_message(offer)
    assert offer.product_link in msg


def test_message_keeps_hook_and_title_prefix():
    offer = _load_offer(0)
    offer = offer.__class__(**{**offer.__dict__, "title": "P" * 5000})
    msg = build_message(offer)
    # head truncated but a recognizable prefix + ellipsis remain
    assert msg.startswith("🔥") or msg.startswith("🚨") or msg.startswith("👀") or msg.startswith("💰")
    assert "..." in msg