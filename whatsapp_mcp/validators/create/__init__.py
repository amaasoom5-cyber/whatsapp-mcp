"""
Template Creation Validators

Pydantic validators for WhatsApp Business API template creation payloads.
Each validator enforces Meta's rules for a specific template type.
"""

from .base_validator import BaseTemplateValidator
from .marketing import MarketingTemplateRequestValidator
from .utility import UtilityTemplateRequestValidator
from .carousel import CarouselTemplateRequestValidator
from .catalog import CatalogTemplateRequestValidator
from .checkout import CheckoutTemplateRequestValidator
from .coupon_code import CouponCodeTemplateRequestValidator
from .lto import LTOTemplateRequestValidator
from .mpm import MPMTemplateRequestValidator
from .order_status import OrderStatusTemplateRequestValidator
from .product_card_carousel import ProductCardCarouselTemplateRequestValidator
from .spm import SPMTemplateRequestValidator
from .call_permission import CallPermissionRequestMessageValidator

# Maps template category/type to the correct validator class
VALIDATOR_MAP = {
    "MARKETING": MarketingTemplateRequestValidator,
    "UTILITY": UtilityTemplateRequestValidator,
    "CAROUSEL": CarouselTemplateRequestValidator,
    "CATALOG": CatalogTemplateRequestValidator,
    "ORDER_DETAILS": CheckoutTemplateRequestValidator,
    "COUPON_CODE": CouponCodeTemplateRequestValidator,
    "LTO": LTOTemplateRequestValidator,
    "MPM": MPMTemplateRequestValidator,
    "ORDER_STATUS": OrderStatusTemplateRequestValidator,
    "PRODUCT_CARD_CAROUSEL": ProductCardCarouselTemplateRequestValidator,
    "SPM": SPMTemplateRequestValidator,
    "CALL_PERMISSION": CallPermissionRequestMessageValidator,
}

__all__ = [
    "BaseTemplateValidator",
    "MarketingTemplateRequestValidator",
    "UtilityTemplateRequestValidator",
    "CarouselTemplateRequestValidator",
    "CatalogTemplateRequestValidator",
    "CheckoutTemplateRequestValidator",
    "CouponCodeTemplateRequestValidator",
    "LTOTemplateRequestValidator",
    "MPMTemplateRequestValidator",
    "OrderStatusTemplateRequestValidator",
    "ProductCardCarouselTemplateRequestValidator",
    "SPMTemplateRequestValidator",
    "CallPermissionRequestMessageValidator",
    "VALIDATOR_MAP",
]
