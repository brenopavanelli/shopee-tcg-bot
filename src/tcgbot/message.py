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

# Telegram hard-caps captions at 1024 characters.
_CAPTION_LIMIT = 1024


def _price_block(offer) -> str:
    if offer.discount_rate > 0:
        rate = min(offer.discount_rate, 99)  # guarda contra divisão por zero
        original = offer.price / (1 - rate / 100)
        return f"💵 R$ {offer.price:.2f} (de R$ {original:.2f}, -{offer.discount_rate}%)"
    return f"💵 R$ {offer.price:.2f}"


def _security_block(offer) -> str:
    parts = [f"⭐ {offer.rating:.1f}"]
    if offer.sales:
        parts.append(f"🛍️ {offer.sales} vendidos")
    if offer.is_official_or_preferred:
        parts.append("✅ Loja oficial/preferencial")
    return " | ".join(parts)


def _body_blocks(offer) -> list[str]:
    """The variable-length middle of a message, most-important first."""
    blocks = [offer.title]
    for block in (_price_block(offer), _security_block(offer)):
        if block:
            blocks.append(block)
    return blocks


def build_message(offer) -> str:
    hook = random.choice(HOOKS)
    cta = random.choice(CTAS)
    link = offer.offer_link or offer.product_link

    # The link is the part users actually click — it must never be truncated.
    # Keep hook + CTA + full URL fixed; if the assembled message overflows the
    # Telegram 1024-char caption limit, drop trailing body blocks, then shrink
    # the title, so the clickable offer URL always survives intact.
    footer = f"\n\n{cta}\n{link}"
    capacity = _CAPTION_LIMIT - len(hook) - len(footer) - 2  # "-2" for the blank line

    body = "\n".join(_body_blocks(offer))
    blocks = _body_blocks(offer)

    if len(body) > capacity:
        # Drop trailing blocks until the title + first block fits.
        while len(blocks) > 1 and len("\n".join(blocks)) > capacity:
            blocks = blocks[:-1]
        if len("\n".join(blocks)) > capacity:
            # Still too big: shrink the title, keep the rest.
            blocks[0] = _shrink(blocks[0], capacity - sum(len(b) + 1 for b in blocks[1:]))
        body = "\n".join(blocks)

    return f"{hook}\n\n{body}{footer}"


def _shrink(text: str, capacity: int) -> str:
    """Shrink *text* to fit *capacity*, appending an ellipsis if cut."""
    if len(text) <= capacity:
        return text
    return text[: max(capacity - 3, 0)] + "..."