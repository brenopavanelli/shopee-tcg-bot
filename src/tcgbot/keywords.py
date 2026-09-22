import json
import random
from pathlib import Path


def _load_state(path: Path) -> dict:
    if not path.exists():
        return {"order": [], "index": 0}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def next_keyword(keywords: list[str], state_path: Path) -> str:
    """Embaralha as keywords e percorre todas antes de repetir qualquer uma."""
    state = _load_state(state_path)

    if not state["order"] or state["index"] >= len(state["order"]):
        order = keywords.copy()
        random.shuffle(order)
        state = {"order": order, "index": 0}

    keyword = state["order"][state["index"]]
    state["index"] += 1
    _save_state(state_path, state)
    return keyword