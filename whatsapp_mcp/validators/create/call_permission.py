from typing import Any, List, Literal, Optional, Union

from whatsapp_mcp.models.body import BodyComponent
from whatsapp_mcp.models.buttons import CallPermissionButton

from .base_validator import BaseTemplateValidator


class CallPermissionRequestMessageValidator(BaseTemplateValidator):
    """
    Base class for template validators.
    """
    components: List[Union[BodyComponent,CallPermissionButton]]

    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
        

