import hashlib
import json
import logging
import os
import time
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

DRY_RUN_FILE = Path(__file__).resolve().parents[2] / "data" / "dry_run_offers.json"
GRAPHQL_ENDPOINT = "https://open-api.affiliate.shopee.com.br/graphql"

QUERY = """
query ProductOffer($keyword: String, $sortType: Int, $page: Int, $limit: Int) {
  productOfferV2(keyword: $keyword, sortType: $sortType, page: $page, limit: $limit) {
    nodes {
      itemId
      shopId
      productName
      priceMin
      priceDiscountRate
      ratingStar
      sales
      shopType
      imageUrl
      productLink
      offerLink
    }
    pageInfo {
      page
      limit
      hasNextPage
    }
  }
}
"""


def build_signature(app_id: str, secret: str, timestamp: int, payload: str) -> str:
    """Carimbo exigido pela Shopee: SHA256 de AppId+Timestamp+Payload+Secret."""
    base = f"{app_id}{timestamp}{payload}{secret}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def build_auth_header(app_id: str, secret: str, timestamp: int, payload: str) -> str:
    signature = build_signature(app_id, secret, timestamp, payload)
    return f"SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}"


def _fetch_real(keyword: str, page: int = 1, limit: int = 20, sort_type: int = 2) -> list[dict]:
    app_id = os.environ["SHOPEE_APP_ID"]
    secret = os.environ["SHOPEE_APP_SECRET"]

    variables = {"keyword": keyword, "sortType": sort_type, "page": page, "limit": limit}
    payload = json.dumps({"query": QUERY, "variables": variables}, separators=(",", ":"))
    timestamp = int(time.time())

    headers = {
        "Content-Type": "application/json",
        "Authorization": build_auth_header(app_id, secret, timestamp, payload),
    }

    try:
        response = requests.post(GRAPHQL_ENDPOINT, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Falha ao chamar a Shopee: %s", exc)
        return []

    body = response.json()
    if "errors" in body:
        logger.error("Shopee retornou erro: %s", body["errors"])
        return []

    return body["data"]["productOfferV2"]["nodes"]


def search_offers(keyword: str, dry_run: bool = True) -> list[dict]:
    if dry_run:
        data = json.loads(DRY_RUN_FILE.read_text(encoding="utf-8"))
        return data["data"]["productOfferV2"]["nodes"]

    return _fetch_real(keyword)