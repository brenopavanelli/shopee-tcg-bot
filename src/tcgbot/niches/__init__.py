"""Niche-aware keyword catalog for the Shopee TCG bot.

A :class:`Niche` bundles a curated search-keyword list under a stable name.
The collector picks a niche via the ``SHOPEE_NICHE`` env var (see
:func:`tcgbot.config`), so the bot can be pointed at different card games
without editing code or the ``KEYWORDS`` env var.

A niche's keywords are stored as a :class:`tuple` so the curated catalog is
immutable at runtime — a bug can't silently mutate the defaults.
"""

from __future__ import annotations

from dataclasses import dataclass, field

_KNOWN: dict[str, Niche] = {}


@dataclass(frozen=True)
class Niche:
    """A named bundle of curated search keywords.

    Attributes:
        name: Stable identifier, e.g. ``"pokemon"``. Matches ``SHOPEE_NICHE``.
        keywords: Curated search keyword list for this card game.
    """

    name: str
    keywords: tuple[str, ...] = field(default_factory=tuple)


def _register(niche: Niche) -> Niche:
    _KNOWN[niche.name] = niche
    return niche


# Curated keyword lists. Add new games here; no other code needs to change.
POKEMON = _register(Niche(
    name="pokemon",
    keywords=(
        "Pokemon TCG",
        "Pokemon booster box",
        "Pokemon Elite Trainer Box",
        "Pokemon TCG Tin",
        "Pokemon sleeve",
        "Pokemon deck box",
        "Pokemon TCG booster",
        "Pokemon TCG blister",
    ),
))

YUGIOH = _register(Niche(
    name="yugioh",
    keywords=(
        "Yu-Gi-Oh Box",
        "Yu-Gi-Oh Deck",
        "Yu-Gi-Oh Booster",
        "Yu-Gi-Oh sleeve",
        "Yu-Gi-Oh tin",
        "Yu-Gi-Oh Structure Deck",
    ),
))

ONE_PIECE = _register(Niche(
    name="one-piece",
    keywords=(
        "One Piece TCG",
        "One Piece Booster Box",
        "One Piece TCG Deck",
        "One Piece sleeve",
        "One Piece Starter Deck",
    ),
))


def known_niches() -> list[str]:
    """Return the stable names of every registered niche, sorted."""
    return sorted(_KNOWN)


def get_niche(name: str) -> Niche:
    """Return the registered niche by exact name.

    Raises:
        KeyError: If ``name`` is not a known niche name.
    """
    return _KNOWN[name]


def resolve_keywords(name: str | None, fallback: list[str] | None = None) -> list[str]:
    """Resolve a niche name to its keyword list.

    The lookup is case-insensitive and ignores ``-``/``_``/whitespace, so
    ``"YU-GI-OH"`` and ``"yugioh"`` both select the Yu-Gi-Oh! catalog.

    Args:
        name: Requested niche name. ``None``/empty falls back to *fallback*.
        fallback: Keyword list returned when *name* is falsy. If not supplied,
            defaults to :data:`POKEMON`'s keywords.

    Returns:
        The keyword list for *name*, or the fallback for ``None``/empty.

    Raises:
        KeyError: If *name* is a non-empty unknown niche name.
    """
    if not name:
        return list(fallback or POKEMON.keywords)
    canonical = _canonicalize(name)
    for registered, niche in _KNOWN.items():
        if _canonicalize(registered) == canonical:
            return list(niche.keywords)
    raise KeyError(name)


def _canonicalize(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())