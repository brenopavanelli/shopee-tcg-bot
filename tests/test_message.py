import json
from pathlib import Path
from tcgbot.models import Offer
from tcgbot.message import build_message

FIXTURE = Path(__file__).parent / "fixtures" / "product_offer_sample.json"


def _load_offer(index: int) -> Offer:
    data = json.loads(FIXTURE.read_text())
    node = data["data"]["productOfferV2"]["nodes"][index]
    return Offer.from_api_node(node)


def test_message_contains_title_and_link():
    offer = _load_offer(0)
    msg = build_message(offer)
    assert offer.title in msg
    assert offer.offer_link in msg


def test_message_respects_telegram_caption_limit():
    offer = _load_offer(0)
    msg = build_message(offer)
    assert len(msg) <= 1024