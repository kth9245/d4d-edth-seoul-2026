# Port note: the real modules/sensing/__init__.py keeps `normalize` and ADDS this line and name.
from modules.sensing.actions.observe_targets import observe_targets as observe

__all__ = ["observe"]
