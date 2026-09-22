import logging
import os

import requests

logger = logging.getLogger(__name__)


def _send_real(message: str, image_url: str) -> bool:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendPhoto"

    try:
        response = requests.post(
            url,
            data={"chat_id": chat_id, "photo": image_url, "caption": message},
            timeout=15,
        )
        response.raise_for_status()
        body = response.json()
    except requests.RequestException as exc:
        logger.error("Falha ao enviar para o Telegram: %s", exc)
        return False

    if not body.get("ok"):
        logger.error("Telegram recusou o envio: %s", body)
        return False

    return True


def send_offer(message: str, image_url: str, dry_run: bool = True) -> bool:
    if dry_run:
        logger.info("[DRY-RUN] Mensagem que seria enviada:\n%s\nImagem: %s", message, image_url)
        return True

    return _send_real(message, image_url)