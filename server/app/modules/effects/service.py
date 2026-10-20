REGISTRY = [
    {
        "id": "brightness",
        "parameters": {"value": {"minimum": -1, "maximum": 1}},
        "implementation": "MLT brightness filter",
        "limitations": "Static level per clip",
    },
    {
        "id": "contrast",
        "parameters": {"value": {"minimum": 0, "maximum": 4}},
        "implementation": "MLT contrast filter",
        "limitations": "Static level per clip",
    },
    {
        "id": "saturation",
        "parameters": {"value": {"minimum": 0, "maximum": 3}},
        "implementation": "MLT saturation filter",
        "limitations": "Static level per clip",
    },
    {
        "id": "zoom",
        "parameters": {"value": {"minimum": 1, "maximum": 4}},
        "implementation": "MLT affine filter",
        "limitations": "Static digital zoom; no subject tracking",
    },
    {
        "id": "pan",
        "parameters": {"value": {"minimum": -1, "maximum": 1}},
        "implementation": "MLT affine filter",
        "limitations": "Static frame-relative pan",
    },
    {
        "id": "tilt",
        "parameters": {"value": {"minimum": -1, "maximum": 1}},
        "implementation": "MLT affine filter",
        "limitations": "Static frame-relative tilt",
    },
    {
        "id": "blur",
        "parameters": {"sigma": {"minimum": 0, "maximum": 20}},
        "implementation": "MLT boxblur filter",
        "limitations": "Uniform blur; no masks",
    },
]


def list_effects():
    return REGISTRY
