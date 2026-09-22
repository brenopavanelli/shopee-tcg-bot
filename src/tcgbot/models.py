from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Offer:
    item_id: int
    shop_id: int
    title: str
    price: float
    rating: Optional[float]
    sales: int
    shop_type: list[int]  # 1=oficial, 2=preferred, 4=preferred plus
    image_url: str
    product_link: str
    offer_link: str
    discount_rate: int = 0

    @property
    def is_official_or_preferred(self) -> bool:
        return any(t in (1, 2, 4) for t in self.shop_type)

    @classmethod
    def from_api_node(cls, node: dict) -> "Offer":
        rating_raw = node.get("ratingStar")
        return cls(
            item_id=int(node["itemId"]),
            shop_id=int(node["shopId"]),
            title=node["productName"],
            price=float(node["priceMin"]),
            rating=float(rating_raw) if rating_raw not in (None, "") else None,
            sales=int(node.get("sales", 0)),
            shop_type=node.get("shopType", []),
            image_url=node.get("imageUrl", ""),
            product_link=node.get("productLink", ""),
            offer_link=node.get("offerLink", ""),
            discount_rate=int(node.get("priceDiscountRate", 0)),
        )