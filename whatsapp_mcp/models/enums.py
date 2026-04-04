"""
Enums for WhatsApp Template Validation
"""

from enum import Enum


class ParameterFormat(str, Enum):
    """Parameter format types supported by META"""
    NAMED = "NAMED"
    POSITIONAL = "POSITIONAL"


class HeaderFormat(str, Enum):
    """Header format types"""
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"
    LOCATION = "LOCATION"


class ButtonType(str, Enum):
    """Button types supported in templates"""
    URL = "url"
    PHONE_NUMBER = "phone_number"
    QUICK_REPLY = "quick_reply"
    COPY_CODE = "copy_code"
    FLOW = "flow"
    CATALOG = "CATALOG"


class ComponentType(str, Enum):
    """Component types in a template"""
    HEADER = "HEADER"
    BODY = "BODY"
    FOOTER = "FOOTER"
    BUTTONS = "BUTTONS"
    CALL_PERMISSION_REQUEST = "call_permission_request"


class TemplateCategory(str, Enum):
    """Template category types"""
    MARKETING = "MARKETING"
    UTILITY = "UTILITY"


class TemplateType(str, Enum):
    """
    Internal template type for tracking what kind of media/content
    the template uses.
    """
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"
    LOCATION = "LOCATION"
    PRODUCT = "PRODUCT"
    CATALOG = "CATALOG"
    AUDIO = "AUDIO"
    CAROUSEL = "CAROUSEL"
