import logging
import os
from pathlib import Path

from tcgbot.config import config
from tcgbot.logging_setup import setup_logging
from tcgbot.models import Offer
from tcgbot.filters import evaluate_offer
from tcgbot.dedup import normalize_title, is_duplicate
from tcgbot.storage import load_history, save_history, prune_old, build_record
from tcgbot.keywords import next_keyword
from tcgbot.message import build_message
from tcgbot.shopee_client import search_offers
from tcgbot.telegram_client import send_offer

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
HISTORY_PATH = DATA_DIR / "postados.json"
KEYWORDS_STATE_PATH = DATA_DIR / "keywords_state.json"


def run(shopee_dry_run: bool = True, telegram_dry_run: bool = True) -> None:
    setup_logging()
    logger.info(
        "Execução iniciada (shopee_dry_run=%s, telegram_dry_run=%s)",
        shopee_dry_run, telegram_dry_run,
    )

    history = prune_old(load_history(HISTORY_PATH), config.title_dedup_days)
    published = False

    for attempt in range(1, config.max_search_attempts + 1):
        keyword = next_keyword(config.keywords, KEYWORDS_STATE_PATH)
        raw_offers = search_offers(keyword, dry_run=shopee_dry_run)
        logger.info("Tentativa %d | keyword=%s | %d produtos recebidos", attempt, keyword, len(raw_offers))

        for node in raw_offers:
            offer = Offer.from_api_node(node)
            norm_title = normalize_title(offer.title)

            dup, dup_reason = is_duplicate(offer.item_id, norm_title, history)
            if dup:
                logger.info("Descartado (%s): %s", dup_reason, offer.title)
                continue

            result = evaluate_offer(offer, config)
            if not result.passed:
                logger.info("Descartado (%s): %s", result.reason, offer.title)
                continue

            message = build_message(offer)
            if send_offer(message, offer.image_url, dry_run=telegram_dry_run):
                history.append(build_record(offer, keyword, norm_title))
                save_history(HISTORY_PATH, history)
                logger.info("Publicado [%s]: %s", result.tier, offer.title)
                published = True
                break

        if published:
            break

    if not published:
        logger.info("Nenhuma oferta válida encontrada nesta execução")

    logger.info("Execução finalizada")


if __name__ == "__main__":
    shopee_dry_run = os.getenv("SHOPEE_DRY_RUN", "true").lower() != "false"
    telegram_dry_run = os.getenv("TELEGRAM_DRY_RUN", "true").lower() != "false"
    run(shopee_dry_run=shopee_dry_run, telegram_dry_run=telegram_dry_run)