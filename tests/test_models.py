import json
from pathlib import Path
from tcgbot.models import Offer

FIXTURE = Path(__file__).parent / "fixtures" / "product_offer_sample.json"


def _load_nodes():
    data = json.loads(FIXTURE.read_text())
    return data["data"]["productOfferV2"]["nodes"]


def test_from_api_node_parses_ideal_offer():
    node = _load_nodes()[0]
    offer = Offer.from_api_node(node)
    assert offer.item_id == 27391045821
    assert offer.rating == 4.9
    assert offer.is_official_or_preferred is True


def test_from_api_node_handles_empty_shop_type():
    node = _load_nodes()[1]
    offer = Offer.from_api_node(node)
    assert offer.shop_type == []
    assert offer.is_official_or_preferred is False