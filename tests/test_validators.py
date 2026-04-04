"""
Tests for Pydantic validators — template creation and sending.
"""

import pytest
from pydantic import ValidationError

from whatsapp_mcp.validators.create import VALIDATOR_MAP
from whatsapp_mcp.validators.send import SEND_VALIDATOR_MAP


# ═══════════════════════════════════════════════════════════════════
# CREATE VALIDATORS
# ═══════════════════════════════════════════════════════════════════


class TestMarketingValidator:
    """Test MarketingTemplateRequestValidator."""

    validator = VALIDATOR_MAP["MARKETING"]

    def test_valid_text_template(self):
        self.validator(
            name="hello_world",
            category="MARKETING",
            language="en",
            components=[{"type": "body", "text": "Hello {{1}}!", "example": {"body_text": [["World"]]}}],
        )

    def test_valid_with_header_footer_buttons(self):
        self.validator(
            name="sale_promo",
            category="MARKETING",
            language="en",
            components=[
                {"type": "header", "format": "TEXT", "text": "Big Sale!"},
                {"type": "body", "text": "Get 50% off on all items."},
                {"type": "footer", "text": "Limited time offer"},
                {"type": "buttons", "buttons": [{"type": "quick_reply", "text": "Shop Now"}]},
            ],
        )

    def test_empty_name_fails(self):
        with pytest.raises(ValidationError):
            self.validator(
                name="",
                category="MARKETING",
                language="en",
                components=[{"type": "body", "text": "Hello"}],
            )

    def test_invalid_name_chars_fails(self):
        with pytest.raises(ValidationError):
            self.validator(
                name="Hello World!",
                category="MARKETING",
                language="en",
                components=[{"type": "body", "text": "Hello"}],
            )

    def test_empty_components_fails(self):
        with pytest.raises(ValidationError):
            self.validator(
                name="test",
                category="MARKETING",
                language="en",
                components=[],
            )

    def test_body_too_long_fails(self):
        with pytest.raises(ValidationError):
            self.validator(
                name="test",
                category="MARKETING",
                language="en",
                components=[{"type": "body", "text": "x" * 1025}],
            )


class TestUtilityValidator:
    """Test UtilityTemplateRequestValidator."""

    validator = VALIDATOR_MAP["UTILITY"]

    def test_valid_utility(self):
        self.validator(
            name="order_update",
            category="UTILITY",
            language="en",
            components=[
                {"type": "body", "text": "Your order {{1}} has been shipped.", "example": {"body_text": [["ORD-123"]]}},
            ],
        )

    def test_wrong_category_fails(self):
        with pytest.raises(ValidationError):
            self.validator(
                name="test",
                category="INVALID",
                language="en",
                components=[{"type": "body", "text": "Hello"}],
            )


class TestCarouselValidator:
    """Test CarouselTemplateRequestValidator."""

    validator = VALIDATOR_MAP["CAROUSEL"]

    def test_valid_carousel(self):
        self.validator(
            name="product_showcase",
            category="MARKETING",
            language="en",
            components=[
                {"type": "body", "text": "Check out our products!"},
                {"type": "carousel", "cards": [
                    {
                        "components": [
                            {"type": "header", "format": "IMAGE", "example": {"header_handle": ["handle1"]}},
                            {"type": "body", "text": "Product 1 - {{1}}", "example": {"body_text": [["$10"]]}},
                            {"type": "buttons", "buttons": [{"type": "quick_reply", "text": "Buy"}]},
                        ]
                    },
                    {
                        "components": [
                            {"type": "header", "format": "IMAGE", "example": {"header_handle": ["handle2"]}},
                            {"type": "body", "text": "Product 2 - {{1}}", "example": {"body_text": [["$20"]]}},
                            {"type": "buttons", "buttons": [{"type": "quick_reply", "text": "Buy"}]},
                        ]
                    },
                ]},
            ],
        )


class TestCatalogValidator:
    """Test CatalogTemplateRequestValidator."""

    validator = VALIDATOR_MAP["CATALOG"]

    def test_valid_catalog(self):
        self.validator(
            name="product_catalog",
            category="MARKETING",
            language="en",
            components=[
                {"type": "BODY", "text": "Browse our catalog!"},
                {"type": "BUTTONS", "buttons": [{"type": "CATALOG", "text": "View catalog"}]},
            ],
        )

    def test_valid_catalog_lowercase(self):
        self.validator(
            name="product_catalog",
            category="MARKETING",
            language="en",
            components=[
                {"type": "body", "text": "Browse our catalog!"},
                {"type": "buttons", "buttons": [{"type": "CATALOG", "text": "View catalog"}]},
            ],
        )


class TestValidatorMap:
    """Test the VALIDATOR_MAP has all expected entries."""

    def test_all_types_present(self):
        expected = {
            "MARKETING", "UTILITY", "CAROUSEL", "CATALOG",
            "ORDER_DETAILS", "COUPON_CODE", "LTO", "MPM",
            "ORDER_STATUS", "PRODUCT_CARD_CAROUSEL", "SPM",
            "CALL_PERMISSION",
        }
        assert set(VALIDATOR_MAP.keys()) == expected

    def test_send_types_present(self):
        expected = {
            "MARKETING", "UTILITY", "CAROUSEL", "CATALOG",
            "ORDER_DETAILS", "COUPON_CODE", "LTO", "MPM",
            "ORDER_STATUS", "PRODUCT_CARD_CAROUSEL", "SPM",
        }
        assert set(SEND_VALIDATOR_MAP.keys()) == expected


# ═══════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════


class TestModels:
    """Test data model classes."""

    def test_body_component(self):
        from whatsapp_mcp.models import BodyComponent
        body = BodyComponent(text="Hello world")
        assert body.type == "body"
        assert body.text == "Hello world"

    def test_body_with_params_requires_example(self):
        from whatsapp_mcp.models import BodyComponent
        with pytest.raises(ValidationError):
            BodyComponent(text="Hello {{name}}")

    def test_header_text(self):
        from whatsapp_mcp.models import HeaderComponent
        header = HeaderComponent(format="TEXT", text="Welcome")
        assert header.type == "header"

    def test_header_image_requires_handle(self):
        from whatsapp_mcp.models import HeaderComponent
        with pytest.raises(ValidationError):
            HeaderComponent(format="IMAGE")

    def test_footer(self):
        from whatsapp_mcp.models import FooterComponent
        footer = FooterComponent(text="Reply STOP")
        assert footer.text == "Reply STOP"

    def test_footer_too_long(self):
        from whatsapp_mcp.models import FooterComponent
        with pytest.raises(ValidationError):
            FooterComponent(text="x" * 61)

    def test_url_button(self):
        from whatsapp_mcp.models import URLButton
        btn = URLButton(text="Visit", url="https://example.com")
        assert btn.type == "url"

    def test_url_button_invalid_url(self):
        from whatsapp_mcp.models import URLButton
        with pytest.raises(ValidationError):
            URLButton(text="Visit", url="not-a-url")

    def test_phone_button(self):
        from whatsapp_mcp.models import PhoneNumberButton
        btn = PhoneNumberButton(text="Call Us", phone_number="+919876543210")
        assert btn.type == "phone_number"

    def test_enums(self):
        from whatsapp_mcp.models.enums import TemplateCategory, TemplateType
        assert TemplateCategory.MARKETING == "MARKETING"
        assert TemplateType.CAROUSEL == "CAROUSEL"
