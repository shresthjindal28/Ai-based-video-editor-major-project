from app.modules.editor.validators import EFFECT_RANGES

REGISTRY = [
    {"id": name, "parameters": {key: {"minimum": limits[0], "maximum": limits[1]} for key, limits in parameters.items()},
     "implementation": "FFmpeg clip preprocessing; MLT composition",
     "keyframes": name in {"pan", "tilt", "zoom"},
     "limitations": "Frame-linear camera animation; no tracking or masks" if name in {"pan", "tilt", "zoom"} else "Static parameters except frame-defined fades"}
    for name, parameters in EFFECT_RANGES.items()
] + [{"id": "lut", "parameters": {"name": {"enum": ["warm", "cool"]}},
      "implementation": "FFmpeg lut3d", "keyframes": False,
      "limitations": "Curated built-in creative LUTs; arbitrary paths and user LUT files are rejected"}]


def list_effects():
    return REGISTRY
