"""
Aimbot activation state helpers.
Supports mouse-button and keyboard-key bindings.
"""

import threading

from src.utils.config import config
from src.utils.mouse import is_button_pressed
from src.utils.mouse import is_key_pressed as backend_is_key_pressed

# Global activation runtime state
_activation_states = {
    "main": {
        "toggle_state": False,
        "use_enable_state": False,
        "last_button_state": False,
        "lock": threading.Lock(),
    },
    "sec": {
        "toggle_state": False,
        "use_enable_state": False,
        "last_button_state": False,
        "lock": threading.Lock(),
    },
}

_ads_states = {
    "main": {
        "toggle_state": False,
        "last_button_state": False,
        "lock": threading.Lock(),
    },
    "sec": {
        "toggle_state": False,
        "last_button_state": False,
        "lock": threading.Lock(),
    },
    "trigger": {
        "toggle_state": False,
        "last_button_state": False,
        "lock": threading.Lock(),
    },
}

_BUTTON_NAME_TO_IDX = {
    "left mouse button": 0,
    "right mouse button": 1,
    "middle mouse button": 2,
    "side mouse 4 button": 3,
    "side mouse 5 button": 4,
}

def _normalize_button_idx(button_idx):
    if button_idx is None:
        return None
    try:
        return int(button_idx)
    except Exception:
        key = str(button_idx).strip().lower()
        return _BUTTON_NAME_TO_IDX.get(key, None)


def _is_keyboard_pressed(key) -> bool:
    if key is None:
        return False
    try:
        return bool(backend_is_key_pressed(key))
    except Exception:
        return False


def is_binding_pressed(binding) -> bool:
    """Check mouse/keyboard binding pressed state."""
    normalized_idx = _normalize_button_idx(binding)
    if normalized_idx is not None:
        try:
            return bool(is_button_pressed(normalized_idx))
        except Exception:
            return False
    return _is_keyboard_pressed(binding)


def _to_positive_float(value, fallback):
    try:
        parsed = float(value)
    except Exception:
        return float(fallback)
    if parsed <= 0:
        return float(fallback)
    return parsed


def _is_ads_trigger_active(current_pressed: bool, ads_key_type: str, state_key: str = "main") -> bool:
    key = str(state_key).strip().lower()
    if key not in _ads_states:
        key = "main"
    state = _ads_states[key]
    mode = str(ads_key_type or "hold").strip().lower()

    with state["lock"]:
        last_pressed = bool(state["last_button_state"])

        if mode == "toggle":
            if current_pressed and not last_pressed:
                state["toggle_state"] = not bool(state["toggle_state"])
            result = bool(state["toggle_state"])
        else:
            # Hold mode: pressed means ADS active.
            state["toggle_state"] = False
            result = bool(current_pressed)

        state["last_button_state"] = bool(current_pressed)

    return result


def get_active_aim_fov(is_sec: bool = False, fallback: float = 0.0) -> float:
    """Resolve runtime FOV with ADS override when ADS key is pressed."""
    base_fallback = max(float(fallback), 1.0)

    if is_sec:
        base_fov = _to_positive_float(getattr(config, "fovsize_sec", base_fallback), base_fallback)
        ads_enabled = bool(getattr(config, "ads_fov_enabled_sec", False))
        ads_key = getattr(config, "ads_key_sec", "")
        ads_key_type = getattr(config, "ads_key_type_sec", "hold")
        ads_fov = _to_positive_float(getattr(config, "ads_fovsize_sec", base_fov), base_fov)
    else:
        base_fov = _to_positive_float(getattr(config, "fovsize", base_fallback), base_fallback)
        ads_enabled = bool(getattr(config, "ads_fov_enabled", False))
        ads_key = getattr(config, "ads_key", "")
        ads_key_type = getattr(config, "ads_key_type", "hold")
        ads_fov = _to_positive_float(getattr(config, "ads_fovsize", base_fov), base_fov)

    if not ads_enabled:
        return base_fov
    state_key = "sec" if is_sec else "main"
    if not _is_ads_trigger_active(is_binding_pressed(ads_key), ads_key_type, state_key=state_key):
        return base_fov
    return ads_fov


def get_active_trigger_fov(fallback: float = 0.0) -> float:
    """Resolve runtime Trigger FOV with ADS override when Trigger ADS key is active."""
    base_fallback = max(float(fallback), 1.0)
    base_fov = _to_positive_float(getattr(config, "tbfovsize", base_fallback), base_fallback)
    ads_enabled = bool(getattr(config, "trigger_ads_fov_enabled", False))
    ads_key = getattr(config, "trigger_ads_key", "")
    ads_key_type = getattr(config, "trigger_ads_key_type", "hold")
    ads_fov = _to_positive_float(getattr(config, "trigger_ads_fovsize", base_fov), base_fov)

    if not ads_enabled:
        return base_fov
    if not _is_ads_trigger_active(is_binding_pressed(ads_key), ads_key_type, state_key="trigger"):
        return base_fov
    return ads_fov


def check_aimbot_activation(button_idx, activation_type: str, is_sec: bool = False) -> bool:
    """
    Check if aimbot should be active for current frame.

    Args:
        button_idx: Mouse button idx/name or keyboard key token/name.
        activation_type: "hold_enable", "hold_disable", "toggle", "use_enable".
        is_sec: Whether this is sec aimbot state.

    Returns:
        bool: True if active.
    """
    current_pressed = bool(is_binding_pressed(button_idx))

    key = "sec" if is_sec else "main"
    state = _activation_states[key]

    with state["lock"]:
        last_pressed = state["last_button_state"]

        if activation_type == "hold_enable":
            result = current_pressed

        elif activation_type == "hold_disable":
            result = not current_pressed

        elif activation_type == "toggle":
            if not last_pressed and current_pressed:
                state["toggle_state"] = not state["toggle_state"]
            result = state["toggle_state"]

        elif activation_type == "use_enable":
            if not last_pressed and current_pressed:
                state["use_enable_state"] = not state["use_enable_state"]
            result = state["use_enable_state"]

        else:
            result = current_pressed

        state["last_button_state"] = current_pressed

    return result


def reset_activation_state(is_sec: bool = False):
    """Reset activation runtime state."""
    key = "sec" if is_sec else "main"
    state = _activation_states[key]
    with state["lock"]:
        state["toggle_state"] = False
        state["use_enable_state"] = False
        state["last_button_state"] = False
