from typing import Literal

from pydantic import BaseModel, ConfigDict


class RenderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    preset: Literal["preview", "1080p_landscape", "1080p_portrait", "1080p_square"] = "preview"
