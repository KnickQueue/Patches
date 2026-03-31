#!/usr/bin/env bash

# IQ.Pilot SSH Revert Tool
# Usage: ./undo_deploy.sh [DEVICE_IP]

IP=$1
if [ -z "$IP" ]; then
    echo "Usage: ./undo_deploy.sh [DEVICE_IP]"
    exit 1
fi

echo "--- Reverting all IQ.Pilot Deployment Changes from $IP ---"

# 1. Push Revert Script
echo "[1/2] Uploading revert and safety tool..."
scp revert.sh iq_pilot_base.patch pq_optimizations.patch high_torque_pq.patch comma@$IP:/data/openpilot/

# 2. Execute Revert
echo "[2/2] Running Revert Script and restoring system defaults..."
ssh comma@$IP "chmod +x /data/openpilot/revert.sh && /data/openpilot/revert.sh"

echo ""
echo "Revert Complete! Rebooting device..."
ssh root@$IP "reboot"
