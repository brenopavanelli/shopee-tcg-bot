import json
from pathlib import Path
from tcgbot.models import Offer
from tcgbot.config import Config
from tcgbot.filters import evaluate_offer

FIXTURE = Path(__file__).parent / "fixtures" / "product_offer_sample.json"


def _load_offers():
    data = json.loads(FIXTURE.read_text())
    nodes = data["data"]["productOfferV2"]["nodes"]
    return [Offer.from_api_node(n) for n in nodes]


def test_ideal_offer_passes_on_ideal_tier():
    offers = _load_offers()
    cfg = Config()
    result = evaluate_offer(offers[0], cfg)
    assert result.passed is True
    assert result.tier == "ideal"


def test_borderline_offer_passes_on_fallback_tier():
    offers = _load_offers()
    cfg = Config()
    result = evaluate_offer(offers[1], cfg)
    assert result.passed is True
    assert result.tier == "fallback"


def test_offer_without_rating_is_rejected():
    offers = _load_offers()
    offer_no_rating = offers[0].__class__(
        **{**offers[0].__dict__, "rating": None}
    )
    cfg = Config()
    result = evaluate_offer(offer_no_rating, cfg)
    assert result.passed is False