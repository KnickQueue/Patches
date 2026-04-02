#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT="${1:-/data/openpilot}"
PATCH_ROOT="/data/Patches"
OVERLAY_DIR="$PATCH_ROOT/iqpilot/pq_iqpilot_overlay_2026-04-02"

cd /data
rm -rf "$PATCH_ROOT"
git clone --single-branch --branch codex/pq-iqpilot-overlay-2026-04-02 https://github.com/KnickQueue/Patches.git "$PATCH_ROOT"
rsync -a "$OVERLAY_DIR/files/" "$TARGET_ROOT/"
python3 -m py_compile \
  "$TARGET_ROOT/selfdrive/ui/iqpilot/layouts/settings/vehicle/brands/volkswagen.py" \
  "$TARGET_ROOT/selfdrive/ui/iqpilot/layouts/settings/steering_sub_layouts/lane_change_settings.py" \
  "$TARGET_ROOT/selfdrive/ui/iqpilot/layouts/settings/steering_sub_layouts/torque_settings.py" \
  "$TARGET_ROOT/iqpilot/selfdrive/locationd/torqued_ext.py" \
  "$TARGET_ROOT/opendbc_repo/opendbc/car/volkswagen/interface.py" \
  "$TARGET_ROOT/opendbc_repo/opendbc/car/volkswagen/carcontroller.py" \
  "$TARGET_ROOT/selfdrive/monitoring/dmonitoringd.py" \
  "$TARGET_ROOT/selfdrive/ui/iqpilot/ui_state.py" \
  "$TARGET_ROOT/selfdrive/ui/layouts/settings/toggles.py" \
  "$TARGET_ROOT/selfdrive/ui/widgets/prime.py" \
  "$TARGET_ROOT/selfdrive/ui/layouts/sidebar.py" \
  "$TARGET_ROOT/selfdrive/ui/mici/layouts/settings/device.py"
echo "Deployed overlay into $TARGET_ROOT"
