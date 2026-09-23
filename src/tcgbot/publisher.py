import logging
import os

from tcgbot.config import config
from tcgbot.logging_setup import setup_logging
from tcgbot.models import Offer
from tcgbot.dedup import normalize_title
from tcgbot.storage import load_history, save_history, prune_old, build_record
from tcgbot.message import build_message
from tcgbot.telegram_client import send_offer
from tcgbot.queue_store import load_queue, save_queue, prune_expired, pop_next
from tcgbot.collector import collect, QUEUE_PATH, HISTORY_PATH

logger = logging.getLogger(__name__)


def publish(shopee_dry_run: bool = True, telegram_dry_run: bool = True) -> bool:
    setup_logging()
    queue = prune_expired(load_queue(QUEUE_PATH), config.queue_max_age_hours)

    if not queue:
        logger.info("Fila vazia — coletando na hora")
        collect(shopee_dry_run=shopee_dry_run)
        queue = prune_expired(load_queue(QUEUE_PATH), config.queue_max_age_hours)

    if not queue:
        logger.info("Nenhuma oferta disponível mesmo após coleta de emergência")
        return False

    item, remaining = pop_next(queue)
    offer = Offer(**item["offer"])
    message = build_message(offer)

    if not send_offer(message, offer.image_url, dry_run=telegram_dry_run):
        logger.error("Falha ao enviar ao Telegram — item permanece na fila")
        return False

    save_queue(QUEUE_PATH, remaining)
    history = prune_old(load_history(HISTORY_PATH), config.title_dedup_days)
    history.append(build_record(offer, item["keyword"], normalize_title(offer.title)))
    save_history(HISTORY_PATH, history)

    logger.info("Publicado: %s | restantes na fila: %d", offer.title, len(remaining))
    return True


if __name__ == "__main__":
    shopee_dry = os.getenv("SHOPEE_DRY_RUN", "true").lower() != "false"
    telegram_dry = os.getenv("TELEGRAM_DRY_RUN", "true").lower() != "false"
    publish(shopee_dry_run=shopee_dry, telegram_dry_run=telegram_dry)