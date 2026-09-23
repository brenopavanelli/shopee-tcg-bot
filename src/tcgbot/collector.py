import logging
import os
from pathlib import Path

from tcgbot.config import config
from tcgbot.logging_setup import setup_logging
from tcgbot.models import Offer
from tcgbot.filters import evaluate_offer
from tcgbot.dedup import normalize_title, is_duplicate
from tcgbot.storage import load_history, prune_old
from tcgbot.keywords import next_keyword
from tcgbot.shopee_client import search_offers
from tcgbot.queue_store import load_queue, save_queue, prune_expired, enqueue

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
HISTORY_PATH = DATA_DIR / "postados.json"
QUEUE_PATH = DATA_DIR / "fila.json"
KEYWORDS_STATE_PATH = DATA_DIR / "keywords_state.json"


def collect(shopee_dry_run: bool = True) -> int:
    history = prune_old(load_history(HISTORY_PATH), config.title_dedup_days)
    queue = prune_expired(load_queue(QUEUE_PATH), config.queue_max_age_hours)

    dedup_pool = list(history) + [
        {"item_id": i["offer"]["item_id"], "normalized_title": normalize_title(i["offer"]["title"])}
        for i in queue
    ]

    added = 0
    for attempt in range(1, config.max_search_attempts + 1):
        keyword = next_keyword(config.keywords, KEYWORDS_STATE_PATH)
        raw_offers = search_offers(keyword, dry_run=shopee_dry_run)
        logger.info("Coleta %d | keyword=%s | %d produtos recebidos", attempt, keyword, len(raw_offers))

        for node in raw_offers:
            offer = Offer.from_api_node(node)
            norm_title = normalize_title(offer.title)

            dup, _ = is_duplicate(offer.item_id, norm_title, dedup_pool)
            if dup:
                continue

            result = evaluate_offer(offer, config)
            if not result.passed:
                continue

            queue = enqueue(queue, offer, keyword)
            dedup_pool.append({"item_id": offer.item_id, "normalized_title": norm_title})
            added += 1

    save_queue(QUEUE_PATH, queue)
    logger.info("Coleta finalizada | %d adicionada(s) | fila com %d item(ns)", added, len(queue))
    return added


if __name__ == "__main__":
    setup_logging()
    dry = os.getenv("SHOPEE_DRY_RUN", "true").lower() != "false"
    collect(shopee_dry_run=dry)