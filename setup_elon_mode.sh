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

# Set params for unmetered data
if [ Params != "" ]; then
  # Note: using a simple way to set param if params tool is available,
  # but here we'll just ensure the files exist in /data/params/d/
  echo -n "0" > /data/params/d/GsmMetered
fi

# Set unmetered network for better connectivity
# svc data unmetered-allow-list add <package_name> (if needed)

echo "Elon Mode setup complete."
