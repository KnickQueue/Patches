#!/usr/bin/env bash

# IQ.Pilot SSH Deployment Tool
# Usage: ./deploy.sh [DEVICE_IP]

IP=$1
if [ -z "$IP" ]; then
    echo "Usage: ./deploy.sh [DEVICE_IP]"
    exit 1
fi

echo "--- Deploying IQ.Pilot Optimizations to $IP ---"

# 1. Push patches and scripts
echo "[1/3] Uploading patches and setup scripts..."
scp -o BatchMode=yes iq_pilot_base.patch pq_optimizations.patch high_torque_pq.patch setup_elon_mode.sh comma@$IP:/data/openpilot/

# 2. Apply Base Patch
echo "[2/3] Applying base optimizations (Elon Mode, Performance, Konnect)..."
ssh -o BatchMode=yes comma@$IP "cd /data/openpilot && patch -p0 < iq_pilot_base.patch"

# 3. Run Setup Script (Sets defaults)
echo "[3/3] Initializing parameters and system settings..."
ssh -o BatchMode=yes comma@$IP "chmod +x /data/openpilot/setup_elon_mode.sh && /data/openpilot/setup_elon_mode.sh"

echo ""
echo "Deployment Complete! Rebooting device..."
ssh root@$IP "reboot"
