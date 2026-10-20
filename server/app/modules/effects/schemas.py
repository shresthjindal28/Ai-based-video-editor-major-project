from typing import Any

from pydantic import BaseModel


class EffectDescription(BaseModel):
    id: str
    parameters: dict[str, Any]
    implementation: str
    limitations: str
