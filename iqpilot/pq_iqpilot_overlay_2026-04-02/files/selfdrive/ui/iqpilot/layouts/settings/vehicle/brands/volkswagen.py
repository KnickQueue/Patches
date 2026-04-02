"""
Copyright © IQ.Lvbs, apart of Project Teal Lvbs, All Rights Reserved, licensed under https://konn3kt.com/tos
"""
from .base import BrandSettings
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.iqpilot.widgets.list_view import toggle_item, multiple_button_item, IQListItem
from opendbc.car.volkswagen.values import CAR, VolkswagenFlags


DESCRIPTIONS = {
  'VolkswagenPqFlashedEps': tr_noop(
    'Enable this if your PQ EPS has been patched with pq-flasher or an equivalent calibration patch. '
    'IQ.Pilot will allow steering below the stock software minimum speed after an on-road cycle.'
  ),
  'pqhca5or7Toggle': tr_noop(
    'Use HCA Status 7 instead of Status 5 for steering control on PQ platform vehicles. '
    'This may help with compatibility on some older Volkswagen models.'
  ),
  'AllowLateralWhenLongUnavailable': tr_noop(
    'Allow lateral control (steering) to remain active even when longitudinal control (gas/brake) '
    'is temporarily unavailable due to a cruise control fault.'
  ),
  'VolkswagenPqLongitudinalProfile': tr_noop(
    'Adjust PQ longitudinal response for smoother or sharper gas and brake behavior.'
  ),
}


class VolkswagenSettings(BrandSettings):
  def __init__(self):
    super().__init__()

    self._pq_header = IQListItem(
      title=lambda: tr("PQ Expert Settings"),
      description=lambda: tr("Settings for older PQ racks, flashed EPS configurations, and cruise-fault behavior on Volkswagen PQ cars."),
    )
    self._pq_header.show_description(True)

    self._pq_status = IQListItem(
      title=lambda: tr("PQ Active Status"),
      description=self._get_pq_status_description,
    )
    self._pq_status.show_description(True)

    self.pq_flashed_eps_toggle = toggle_item(
      lambda: tr("PQ EPS Flashed"),
      description=lambda: tr(DESCRIPTIONS["VolkswagenPqFlashedEps"]),
      initial_state=ui_state.params.get_bool("VolkswagenPqFlashedEps"),
      callback=self._on_pq_flashed_eps_toggle,
      enabled=lambda: ui_state.is_offroad(),
    )

    self.pq_hca_toggle = toggle_item(
      lambda: tr("PQ HCA Status 7 Mode"),
      description=lambda: tr(DESCRIPTIONS["pqhca5or7Toggle"]),
      initial_state=ui_state.params.get_bool("pqhca5or7Toggle"),
      callback=self._on_pq_hca_toggle,
      enabled=lambda: ui_state.is_offroad(),
    )

    self.lateral_when_long_unavailable = toggle_item(
      lambda: tr("Lateral Control When Cruise Faulted"),
      description=lambda: tr(DESCRIPTIONS["AllowLateralWhenLongUnavailable"]),
      initial_state=ui_state.params.get_bool("AllowLateralWhenLongUnavailable"),
      callback=self._on_lateral_when_long_unavailable,
      enabled=lambda: ui_state.is_offroad(),
    )

    self.pq_longitudinal_profile = multiple_button_item(
      title=lambda: tr("PQ Longitudinal Feel"),
      description=lambda: tr(DESCRIPTIONS["VolkswagenPqLongitudinalProfile"]),
      buttons=[lambda: tr("Comfort"), lambda: tr("Balanced"), lambda: tr("Responsive")],
      button_width=250,
      selected_index=int(ui_state.params.get("VolkswagenPqLongitudinalProfile", return_default=True) or 1),
      callback=self._on_pq_longitudinal_profile,
      param="VolkswagenPqLongitudinalProfile",
      inline=False,
    )

    self.items = [self._pq_header, self._pq_status, self.pq_hca_toggle, self.pq_flashed_eps_toggle,
                  self.lateral_when_long_unavailable, self.pq_longitudinal_profile]

  def _on_pq_flashed_eps_toggle(self, state: bool):
    ui_state.params.put_bool("VolkswagenPqFlashedEps", state)
    ui_state.params.put_bool("OnroadCycleRequested", True)

  def _is_pq(self) -> bool:
    bundle = ui_state.params.get("CarPlatformBundle")
    if bundle:
      platform = bundle.get("platform")
      if platform:
        try:
          return bool(CAR[platform].config.flags & VolkswagenFlags.PQ)
        except (KeyError, AttributeError):
          return False
    elif ui_state.CP:
      return bool(ui_state.CP.flags & VolkswagenFlags.PQ)
    return False

  def _on_pq_hca_toggle(self, state: bool):
    ui_state.params.put_bool("pqhca5or7Toggle", state)

  def _on_lateral_when_long_unavailable(self, state: bool):
    ui_state.params.put_bool("AllowLateralWhenLongUnavailable", state)

  def _on_pq_longitudinal_profile(self, index: int):
    ui_state.params.put("VolkswagenPqLongitudinalProfile", index)

  @staticmethod
  def _profile_name(index: int) -> str:
    return [tr("Comfort"), tr("Balanced"), tr("Responsive")][max(0, min(index, 2))]

  @staticmethod
  def _state_label(enabled: bool) -> str:
    return tr("On") if enabled else tr("Off")

  def _get_pq_status_description(self):
    profile = int(ui_state.params.get("VolkswagenPqLongitudinalProfile", return_default=True) or 1)
    flashed_eps = ui_state.params.get_bool("VolkswagenPqFlashedEps")
    hca_status = "7" if ui_state.params.get_bool("pqhca5or7Toggle") else "5"
    lat_only = ui_state.params.get_bool("AllowLateralWhenLongUnavailable")
    cycle_pending = ui_state.params.get_bool("OnroadCycleRequested")

    torque_status = tr("Disabled")
    if ui_state.params.get_bool("LiveTorqueParamsToggle"):
      ltp = ui_state.sm["liveTorqueParameters"]
      live_active = bool(getattr(ltp, "useParams", False))
      live_valid = bool(getattr(ltp, "liveValid", False))
      cal_perc = int(getattr(ltp, "calPerc", 0))
      if live_active and live_valid:
        torque_status = tr("Active")
      elif live_active:
        torque_status = tr("Learning")
      else:
        torque_status = tr("Waiting")
      torque_status = f"{torque_status} ({cal_perc}%)"

    cycle_text = tr("Pending") if cycle_pending else tr("Applied")
    return (
      f"{tr('Longitudinal Profile')}: {self._profile_name(profile)}"
      f"<br>{tr('HCA Command Status')}: {hca_status}"
      f"<br>{tr('Flashed EPS Mode')}: {self._state_label(flashed_eps)} ({cycle_text})"
      f"<br>{tr('Cruise-Fault Lateral')}: {self._state_label(lat_only)}"
      f"<br>{tr('Torque Self-Tune')}: {torque_status}"
    )

  def update_settings(self):
    is_pq = self._is_pq()
    disabled_msg = ""
    if is_pq and not ui_state.is_offroad():
      disabled_msg = tr("Enable \"Always Offroad\" in Device panel, or turn vehicle off to change these settings.")

    self._pq_header.set_visible(is_pq)
    self._pq_status.set_visible(is_pq)
    self.pq_flashed_eps_toggle.set_visible(is_pq)
    self.pq_hca_toggle.set_visible(is_pq)
    self.lateral_when_long_unavailable.set_visible(is_pq)
    self.pq_longitudinal_profile.set_visible(is_pq)

    if disabled_msg:
      self.pq_hca_toggle.set_description(f"<b>{disabled_msg}</b><br><br>{tr(DESCRIPTIONS['pqhca5or7Toggle'])}<br><br>{tr('Recommended only if Status 5 causes steering compatibility issues on your rack.')}")
      self.pq_flashed_eps_toggle.set_description(f"<b>{disabled_msg}</b><br><br>{tr(DESCRIPTIONS['VolkswagenPqFlashedEps'])}<br><br>{tr('Use this only on racks already patched outside IQ.Pilot; it does not flash the EPS for you.')}")
      self.lateral_when_long_unavailable.set_description(f"<b>{disabled_msg}</b><br><br>{tr(DESCRIPTIONS['AllowLateralWhenLongUnavailable'])}<br><br>{tr('Helpful if your PQ cruise faults intermittently but steering remains stable.')}")
      self.pq_longitudinal_profile.set_description(f"<b>{disabled_msg}</b><br><br>{tr(DESCRIPTIONS['VolkswagenPqLongitudinalProfile'])}<br><br>{tr('Comfort softens stop-and-go response, Balanced is the default, and Responsive sharpens pedal changes.')}")
    else:
      self.pq_hca_toggle.set_description(lambda: tr(DESCRIPTIONS["pqhca5or7Toggle"]) + "<br><br>" + tr("Recommended only if Status 5 causes steering compatibility issues on your rack."))
      self.pq_flashed_eps_toggle.set_description(lambda: tr(DESCRIPTIONS["VolkswagenPqFlashedEps"]) + "<br><br>" + tr("Use this only on racks already patched outside IQ.Pilot; it does not flash the EPS for you."))
      self.lateral_when_long_unavailable.set_description(lambda: tr(DESCRIPTIONS["AllowLateralWhenLongUnavailable"]) + "<br><br>" + tr("Helpful if your PQ cruise faults intermittently but steering remains stable."))
      self.pq_longitudinal_profile.set_description(lambda: tr(DESCRIPTIONS["VolkswagenPqLongitudinalProfile"]) + "<br><br>" + tr("Comfort softens stop-and-go response, Balanced is the default, and Responsive sharpens pedal changes."))
