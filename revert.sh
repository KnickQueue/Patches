#!/usr/bin/env bash

# IQ.Pilot Reversal & Safety Tool
# This script undoes all patches and resets system parameters to their original states.

echo "--- Reverting IQ.Pilot Optimizations ---"

# 1. Reverse the Source Code Patches (if applied)
echo "[1/4] Reversing source code patches..."
[ -f "iq_pilot_base.patch" ] && patch -R -p0 < iq_pilot_base.patch || echo "Base patch not found or not applied."
[ -f "pq_optimizations.patch" ] && patch -R -p0 < pq_optimizations.patch || echo "PQ optimizations patch not found or not applied."
[ -f "high_torque_pq.patch" ] && patch -R -p0 < high_torque_pq.patch || echo "High torque patch not found or not applied."

# 2. Reset Parameters
echo "[2/4] Resetting system parameters..."
echo -n "0" > /data/params/d/ElonMode
echo -n "0" > /data/params/d/PerformanceMode
echo -n "1" > /data/params/d/GsmMetered

# 3. Restore Network Settings
echo "[3/4] Restoring Network Defaults..."
settings put global data_roaming 0
settings put global tether_dun_required 1
settings put global network_metered_1 1
settings put global network_metered_2 1

# 4. Restore Performance Settings
echo "[4/4] Restoring CPU & I/O Defaults..."
if [ -d /sys/devices/system/cpu/cpufreq ]; then
  echo "schedutil" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null
fi
if [ -f /sys/block/mmcblk0/queue/read_ahead_kb ]; then
  echo "128" | sudo tee /sys/block/mmcblk0/queue/read_ahead_kb > /dev/null
fi
if [ -f /sys/block/nvme0n1/queue/read_ahead_kb ]; then
  echo "128" | sudo tee /sys/block/nvme0n1/queue/read_ahead_kb > /dev/null
fi

echo "--- Revert Complete! System restored to stock settings ---"
