#!/usr/bin/bash

# 1. Ensure parameters are writable
mkdir -p /data/params/d

# Initialize Elon Mode parameters with ON by default
if [ ! -f /data/params/d/ElonMode ]; then
  echo -n "1" > /data/params/d/ElonMode
fi
if [ ! -f /data/params/d/ShowDmDebug ]; then
  echo -n "0" > /data/params/d/ShowDmDebug
fi

# Network optimization settings for Comma hardware
# On AGNOS, the settings binary is in /system/bin/ but might not be in sudo's PATH
SETTINGS="/system/bin/settings"
[ -f "$SETTINGS" ] || SETTINGS="settings"

$SETTINGS put global data_roaming 1
$SETTINGS put global tether_dun_required 0
$SETTINGS put global network_metered_1 0
$SETTINGS put global network_metered_2 0

# 2. Applying Steering and Torque Patches
echo "Applying PQ Smooth Steering fixes..."
patch -N -p0 < pq_optimizations.patch || echo "PQ Smoothness already applied."

echo "Increasing Steering Torque Limit to 4.0 Nm..."
patch -N -p0 < high_torque_pq.patch || echo "High Torque already applied."

# 3. Finalize and Reboot
echo "Elon Mode and PQ Optimizations setup complete."
