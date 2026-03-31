import pytest
from contextlib import contextmanager

from openpilot.system.hardware import HARDWARE, TICI
from openpilot.system.hardware.base import LPAError, LPAProfileNotFoundError, Profile
from openpilot.system.hardware.tici import lpa as lpa_module
from openpilot.system.hardware.tici.esim_manager import EsimManager

# https://euicc-manual.osmocom.org/docs/rsp/known-test-profile
# iccid is always the same for the given activation code
TEST_ACTIVATION_CODE = 'LPA:1$rsp.truphone.com$QRF-BETTERROAMING-PMRDGIR2EARDEIT5'
TEST_ICCID = '8944476500001944011'

TEST_NICKNAME = 'test_profile'

def cleanup():
  lpa = HARDWARE.get_sim_lpa()
  try:
    lpa.delete_profile(TEST_ICCID)
  except LPAProfileNotFoundError:
    pass
  lpa.process_notifications()

class TestEsim:

  @classmethod
  def setup_class(cls):
    if not TICI:
      pytest.skip()
    cleanup()

  @classmethod
  def teardown_class(cls):
    cleanup()

  def test_provision_enable_disable(self):
    lpa = HARDWARE.get_sim_lpa()
    current_active = lpa.get_active_profile()

    lpa.download_profile(TEST_ACTIVATION_CODE, TEST_NICKNAME)
    assert any(p.iccid == TEST_ICCID and p.nickname == TEST_NICKNAME for p in lpa.list_profiles())

    lpa.enable_profile(TEST_ICCID)
    new_active = lpa.get_active_profile()
    assert new_active is not None
    assert new_active.iccid == TEST_ICCID
    assert new_active.nickname == TEST_NICKNAME

    lpa.disable_profile(TEST_ICCID)
    new_active = lpa.get_active_profile()
    assert new_active is None

    if current_active:
      lpa.enable_profile(current_active.iccid)


class TestEsimDeleteHandling:
  def test_delete_ignores_notification_cleanup_if_profile_is_gone(self, monkeypatch):
    target_iccid = "89012804332267989477"
    lpa = lpa_module.TiciLPA()

    monkeypatch.setattr(lpa, "_validate_profile_exists", lambda iccid: None)
    monkeypatch.setattr(lpa, "get_active_profile", lambda: Profile("8901240527117095243", "US Mobile", True, "Wireless"))
    monkeypatch.setattr(lpa, "_restart_modem", lambda: None)
    monkeypatch.setattr(
      lpa,
      "list_profiles",
      lambda: [Profile("8901240527117095243", "US Mobile", True, "Wireless")],
    )

    @contextmanager
    def fake_open_client():
      yield object()

    monkeypatch.setattr(lpa, "_open_client", fake_open_client)
    monkeypatch.setattr(lpa_module, "delete_profile", lambda client, iccid: None)

    def fail_notifications(client):
      raise RuntimeError('AT command failed (AT+CGLA=2,16,"80E2910003BF2800"): AT command failed')

    monkeypatch.setattr(lpa_module, "process_notifications", fail_notifications)

    lpa.delete_profile(target_iccid)

  def test_delete_raises_clear_error_if_profile_still_present_after_cleanup_failure(self, monkeypatch):
    target_iccid = "89012804332267989477"
    lpa = lpa_module.TiciLPA()

    monkeypatch.setattr(lpa, "_validate_profile_exists", lambda iccid: None)
    monkeypatch.setattr(lpa, "get_active_profile", lambda: Profile("8901240527117095243", "US Mobile", True, "Wireless"))
    monkeypatch.setattr(lpa, "_restart_modem", lambda: None)
    monkeypatch.setattr(
      lpa,
      "list_profiles",
      lambda: [
        Profile("8901240527117095243", "US Mobile", True, "Wireless"),
        Profile(target_iccid, "RedPocket", False, "RedPocket"),
      ],
    )

    @contextmanager
    def fake_open_client():
      yield object()

    monkeypatch.setattr(lpa, "_open_client", fake_open_client)
    monkeypatch.setattr(lpa_module, "delete_profile", lambda client, iccid: None)

    def fail_notifications(client):
      raise RuntimeError('AT command failed (AT+CGLA=2,16,"80E2910003BF2800"): AT command failed')

    monkeypatch.setattr(lpa_module, "process_notifications", fail_notifications)

    with pytest.raises(LPAError, match="Profile delete did not finish cleanly"):
      lpa.delete_profile(target_iccid)

  def test_manager_maps_notification_cleanup_error(self):
    error = LPAError('AT command failed (AT+CGLA=2,16,"80E2910003BF2800"): AT command failed')
    assert EsimManager._map_error(error) == "Modem notification cleanup failed; refresh profiles"
