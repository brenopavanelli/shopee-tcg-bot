import random

HOOKS = [
    "🔥 Oferta encontrada!",
    "🚨 Olha esse preço!",
    "👀 Pokémon TCG em promoção!",
    "🔥 Essa oferta merece atenção!",
    "💰 Preço interessante no Pokémon TCG!",
]

CTAS = [
    "🛒 Confira a oferta:",
    "👉 Ver oferta:",
    "🔗 Confira na Shopee:",
    "🔥 Aproveite enquanto estiver disponível:",
]


def _price_block(offer) -> str:
    if offer.discount_rate > 0:
        original = offer.price / (1 - offer.discount_rate / 100)
        return f"💵 R$ {offer.price:.2f} (de R$ {original:.2f}, -{offer.discount_rate}%)"
    return f"💵 R$ {offer.price:.2f}"


def _security_block(offer) -> str:
    parts = [f"⭐ {offer.rating:.1f}"]
    if offer.sales:
        parts.append(f"🛍️ {offer.sales} vendidos")
    if offer.is_official_or_preferred:
        parts.append("✅ Loja oficial/preferencial")
    return " | ".join(parts)


def build_message(offer) -> str:
    hook = random.choice(HOOKS)
    cta = random.choice(CTAS)
    lines = [
        hook,
        "",
        offer.title,
        _price_block(offer),
        _security_block(offer),
        "",
        cta,
        offer.offer_link or offer.product_link,
    ]
    message = "\n".join(lines)
    if len(message) > 1024:
        message = message[:1021] + "..."
    return message