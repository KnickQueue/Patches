#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 user@host [remote_openpilot_path]" >&2
  exit 1
fi

REMOTE="$1"
REMOTE_ROOT="${2:-/data/openpilot}"
PATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE_STAGE="/tmp/pq_iqpilot_overlay_2026-04-02"

echo "Uploading overlay to ${REMOTE}:${REMOTE_STAGE}"
ssh "$REMOTE" "rm -rf '$REMOTE_STAGE' && mkdir -p '$REMOTE_STAGE'"
scp -r "$PATCH_DIR/files" "$REMOTE:$REMOTE_STAGE/"

echo "Applying overlay into ${REMOTE_ROOT}"
ssh "$REMOTE" "cd '$REMOTE_ROOT' && rsync -aR '$REMOTE_STAGE'/./files/ ./"

echo "Running syntax checks"
ssh "$REMOTE" "cd '$REMOTE_ROOT' && python3 -m py_compile \
  selfdrive/ui/iqpilot/layouts/settings/vehicle/brands/volkswagen.py \
  selfdrive/ui/iqpilot/layouts/settings/steering_sub_layouts/lane_change_settings.py \
  selfdrive/ui/iqpilot/layouts/settings/steering_sub_layouts/torque_settings.py \
  iqpilot/selfdrive/locationd/torqued_ext.py \
  opendbc_repo/opendbc/car/volkswagen/interface.py \
  opendbc_repo/opendbc/car/volkswagen/carcontroller.py \
  selfdrive/monitoring/dmonitoringd.py \
  selfdrive/ui/iqpilot/ui_state.py \
  selfdrive/ui/layouts/settings/toggles.py \
  selfdrive/ui/widgets/prime.py \
  selfdrive/ui/layouts/sidebar.py \
  selfdrive/ui/mici/layouts/settings/device.py"

echo "Overlay applied successfully."
echo "Next step: restart manager/UI or reboot the device."
