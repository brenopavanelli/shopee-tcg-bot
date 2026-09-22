from dataclasses import dataclass
from tcgbot.models import Offer
from tcgbot.config import Config


@dataclass(frozen=True)
class FilterResult:
    passed: bool
    reason: str
    tier: str | None = None  # "ideal" ou "fallback"


def _meets_ideal(offer: Offer, cfg: Config) -> bool:
    return (
        offer.rating is not None
        and offer.rating >= cfg.min_rating_ideal
        and offer.sales >= cfg.min_sales_ideal
        and offer.is_official_or_preferred
    )


def _meets_fallback(offer: Offer, cfg: Config) -> bool:
    return (
        offer.rating is not None
        and offer.rating >= cfg.min_rating_fallback
        and offer.sales >= cfg.min_sales_fallback
    )


def evaluate_offer(offer: Offer, cfg: Config) -> FilterResult:
    if offer.rating is None:
        return FilterResult(False, "sem avaliação disponível")

    if _meets_ideal(offer, cfg):
        return FilterResult(True, "atende aos critérios ideais", tier="ideal")

    if _meets_fallback(offer, cfg):
        return FilterResult(True, "atende aos critérios de fallback", tier="fallback")

    return FilterResult(
        False,
        f"não atingiu nota/vendas mínimas (rating={offer.rating}, sales={offer.sales})",
    )