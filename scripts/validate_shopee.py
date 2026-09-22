import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tcgbot.config import config  # noqa: E402  (garante que o .env foi carregado)
from tcgbot.shopee_client import search_offers  # noqa: E402

keyword = sys.argv[1] if len(sys.argv) > 1 else "Pokemon TCG"
nodes = search_offers(keyword, dry_run=False)

print(f"{len(nodes)} produto(s) encontrado(s) para '{keyword}'\n")
if nodes:
    print(json.dumps(nodes[0], indent=2, ensure_ascii=False))