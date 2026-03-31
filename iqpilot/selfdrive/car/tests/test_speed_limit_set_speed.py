from types import SimpleNamespace

import pytest

from cereal import car, custom
from openpilot.common.constants import CV
from openpilot.selfdrive.car.cruise import VCruiseHelper


class TestSpeedLimitSetSpeedMirror:
  def setup_method(self):
    self.CP = car.CarParams(pcmCruise=True, openpilotLongitudinalControl=True)
    self.CP_IQ = custom.IQCarParams(pcmCruiseSpeed=True)
    self.v_cruise_helper = VCruiseHelper(self.CP, self.CP_IQ)

  @staticmethod
  def _iq_plan(limit_mps: float, state) -> SimpleNamespace:
    resolver = SimpleNamespace(
      speedLimitValid=limit_mps > 0,
      speedLimitLastValid=limit_mps > 0,
      speedLimitFinalLast=limit_mps,
    )
    assist = SimpleNamespace(state=state)
    return SimpleNamespace(speedLimit=SimpleNamespace(resolver=resolver, assist=assist))

  def test_op_long_mirrors_active_speed_limit_target_into_cluster_speed(self):
    self.v_cruise_helper.update_speed_limit_assist(False, self._iq_plan(17.88, custom.IQPlan.SpeedLimit.AssistState.active))

    CS = car.CarState(cruiseState={"available": True, "speed": 22.35, "speedCluster": 22.35})
    self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=False)

    assert self.v_cruise_helper.v_cruise_kph == pytest.approx(17.88 * CV.MS_TO_KPH, abs=0.1)
    assert self.v_cruise_helper.v_cruise_cluster_kph == pytest.approx(17.88 * CV.MS_TO_KPH, abs=0.1)

  def test_op_long_keeps_speed_limit_target_as_upper_bound_when_slc_inactive(self):
    self.v_cruise_helper.update_speed_limit_assist(False, self._iq_plan(17.88, custom.IQPlan.SpeedLimit.AssistState.inactive))

    CS = car.CarState(cruiseState={"available": True, "speed": 22.35, "speedCluster": 22.35})
    self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=False)

    assert self.v_cruise_helper.v_cruise_kph == pytest.approx(17.88 * CV.MS_TO_KPH, abs=0.1)
    assert self.v_cruise_helper.v_cruise_cluster_kph == pytest.approx(17.88 * CV.MS_TO_KPH, abs=0.1)

  def test_op_long_allows_lower_manual_set_speed_to_remain_below_limit(self):
    self.v_cruise_helper.update_speed_limit_assist(False, self._iq_plan(17.88, custom.IQPlan.SpeedLimit.AssistState.inactive))

    # First cycle after a valid limit appears will sync to the resolved target.
    CS = car.CarState(cruiseState={"available": True, "speed": 22.35, "speedCluster": 22.35})
    self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=False)

    # On later cycles with the same limit, a lower manual set speed should remain below target.
    CS = car.CarState(cruiseState={"available": True, "speed": 13.41, "speedCluster": 13.41})
    self.v_cruise_helper.update_v_cruise(CS, enabled=True, is_metric=False)

    assert self.v_cruise_helper.v_cruise_kph == pytest.approx(13.41 * CV.MS_TO_KPH, abs=0.1)
    assert self.v_cruise_helper.v_cruise_cluster_kph == pytest.approx(13.41 * CV.MS_TO_KPH, abs=0.1)
