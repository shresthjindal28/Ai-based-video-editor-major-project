"""Public aliases for the versioned timeline API contract."""

from app.modules.editor.schemas import (
    ClipSpec,
    EffectSpec,
    OutputProfile,
    TimelinePlan,
    TransitionSpec,
)

SCHEMA_VERSION = "1"

__all__ = [
    "ClipSpec",
    "EffectSpec",
    "OutputProfile",
    "TimelinePlan",
    "TransitionSpec",
    "SCHEMA_VERSION",
]
