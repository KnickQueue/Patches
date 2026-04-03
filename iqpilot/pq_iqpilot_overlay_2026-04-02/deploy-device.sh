#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT="${1:-/data/openpilot}"
PATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rsync -a "$PATCH_DIR/files/" "$TARGET_ROOT/"
python3 -m py_compile \
  "$TARGET_ROOT/iqpilot/selfdrive/controls/lib/helpers/torque_override.py" \
  "$TARGET_ROOT/iqpilot/selfdrive/controls/lib/helpers/torque_ext.py" \
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
