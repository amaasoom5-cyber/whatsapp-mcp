"""
Template Send Validators

Pydantic validators for WhatsApp Business API template send payloads.
"""

from .base import BaseRequestTemplateValidator
from .marketing import MarketingTemplateSendRequestValidator
from .utility import UtilityTemplateSendRequestValidator
from .carousel import CarouselTemplateSendRequestValidator
from .catalog import CatalogTemplateSendRequestValidator
from .checkout import CheckoutTemplateSendRequestValidator
from .coupon_code import CouponCodeTemplateSendRequestValidator
from .lto import LTOTemplateSendRequestValidator
from .mpm import MPMTemplateSendRequestValidator
from .order_status import OrderStatusTemplateSendRequestValidator
from .product_card_carousel import ProductCardCarouselTemplateSendRequestValidator
from .spm import SPMTemplateSendRequestValidator

# Maps template type to send validator class
SEND_VALIDATOR_MAP = {
    "MARKETING": MarketingTemplateSendRequestValidator,
    "UTILITY": UtilityTemplateSendRequestValidator,
    "CAROUSEL": CarouselTemplateSendRequestValidator,
    "CATALOG": CatalogTemplateSendRequestValidator,
    "ORDER_DETAILS": CheckoutTemplateSendRequestValidator,
    "COUPON_CODE": CouponCodeTemplateSendRequestValidator,
    "LTO": LTOTemplateSendRequestValidator,
    "MPM": MPMTemplateSendRequestValidator,
    "ORDER_STATUS": OrderStatusTemplateSendRequestValidator,
    "PRODUCT_CARD_CAROUSEL": ProductCardCarouselTemplateSendRequestValidator,
    "SPM": SPMTemplateSendRequestValidator,
}

__all__ = [
    "BaseRequestTemplateValidator",
    "MarketingTemplateSendRequestValidator",
    "UtilityTemplateSendRequestValidator",
    "CarouselTemplateSendRequestValidator",
    "CatalogTemplateSendRequestValidator",
    "CheckoutTemplateSendRequestValidator",
    "CouponCodeTemplateSendRequestValidator",
    "LTOTemplateSendRequestValidator",
    "MPMTemplateSendRequestValidator",
    "OrderStatusTemplateSendRequestValidator",
    "ProductCardCarouselTemplateSendRequestValidator",
    "SPMTemplateSendRequestValidator",
    "SEND_VALIDATOR_MAP",
]
