REGISTRY = [
    {"id":"hard_cut", "duration_frames":0, "implementation":"MLT playlist cut"},
    *[{"id": name, "duration_frames":{"min":1,"max":300}, "implementation":"MLT compositor",
       "limitations":"Adjacent clips on the same track must overlap by the transition duration"}
      for name in ("cross_dissolve","wipe","slide")],
]


def list_transitions():
    return REGISTRY
