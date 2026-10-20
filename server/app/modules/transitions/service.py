REGISTRY = [
    {"id": "hard_cut", "duration_frames": 0, "implementation": "MLT playlist cut"},
    {
        "id": "cross_dissolve",
        "duration_frames": {"min": 1, "max": 120},
        "implementation": "MLT luma transition",
    },
    {
        "id": "wipe",
        "duration_frames": {"min": 1, "max": 120},
        "implementation": "MLT luma transition",
    },
]


def list_transitions():
    return REGISTRY
