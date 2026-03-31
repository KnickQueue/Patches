"""
Copyright © IQ.Lvbs, apart of Project Teal Lvbs, All Rights Reserved, licensed under https://konn3kt.com/tos
"""
from __future__ import annotations

from openpilot.common.constants import CV
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX

from opendbc.car import structs

ENHANCED_STOCK_LONGITUDINAL_CONTROL_SET_SPEED_KPH_KEY = "enhancedStockLongitudinalControl.setSpeedKph"


def _float_param(key: str, value: float) -> dict[str, object]:
  return {"key": key, "type": "float", "value": f"{float(value):.3f}".encode("utf-8")}


def build_iq_control_params_from_plan(CP: structs.CarParams, iq_plan, selfdrive_enabled: bool) -> list[dict[str, object]]:
  if not CP.openpilotLongitudinalControl or not selfdrive_enabled:
    return []

  resolver = getattr(getattr(iq_plan, "speedLimit", None), "resolver", None)
  assist = getattr(getattr(iq_plan, "speedLimit", None), "assist", None)
  if resolver is None or assist is None:
    return []

  speed_limit_final_last = float(getattr(resolver, "speedLimitFinalLast", 0.0) or 0.0)
  assist_enabled = bool(getattr(assist, "enabled", False))
  if not assist_enabled or speed_limit_final_last <= 0.0:
    return []

  set_speed_kph = max(0.0, min(V_CRUISE_MAX, speed_limit_final_last * CV.MS_TO_KPH))
  return [_float_param(ENHANCED_STOCK_LONGITUDINAL_CONTROL_SET_SPEED_KPH_KEY, set_speed_kph)]


def get_set_speed_kph_from_params(params) -> float | None:
  for param in params:
    key = param.key if hasattr(param, "key") else param.get("key")
    if key != ENHANCED_STOCK_LONGITUDINAL_CONTROL_SET_SPEED_KPH_KEY:
      continue
    raw_value = param.value if hasattr(param, "value") else param.get("value")
    try:
      raw = raw_value.decode("utf-8") if isinstance(raw_value, (bytes, bytearray)) else str(raw_value)
      value = float(raw)
    except (AttributeError, TypeError, ValueError):
      return None
    return max(0.0, min(V_CRUISE_MAX, value))
  return None
