import re
import unicodedata

_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_SPACE_RE = re.compile(r"\s+")


def normalize_title(title: str) -> str:
    """Deixa o título 'comparável': minúsculo, sem acento, sem emoji/pontuação, sem espaço duplo."""
    text = unicodedata.normalize("NFKD", title)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = _PUNCT_RE.sub(" ", text)
    text = _SPACE_RE.sub(" ", text).strip()
    return text


def is_duplicate(item_id: int, normalized_title: str, history: list[dict]) -> tuple[bool, str]:
    """history já deve vir filtrado (só registros dentro da janela de dias válida)."""
    for record in history:
        if record["item_id"] == item_id:
            return True, "mesmo item_id já publicado"
        if record["normalized_title"] == normalized_title:
            return True, "título normalizado já publicado"
    return False, ""